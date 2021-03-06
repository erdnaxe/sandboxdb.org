# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

import re
import subprocess
import json


def get_services_store_path(channel="nixos-unstable") -> [str]:
    """Return services files store paths.

    You need to have nix with the corresponding channel.
    """
    drv_pattern = re.compile(r"-unit-.*\.service$")

    # Collect all NixOS tests
    nix_tests = set()
    tests_path = f"/nix/var/nix/profiles/per-user/root/channels/{channel}/nixos/tests/all-tests.nix"
    with open(tests_path, "r") as f:
        for line in f.readlines():
            for s in line.strip().split(" "):
                if s.startswith("./") and s.endswith(".nix"):
                    nix_tests.add(s[2:])

    services_drv = set()
    n_tests = len(nix_tests)
    for i, nix_path in enumerate(nix_tests):
        # Instanciate the derivation corresponding to /etc/systemd/system in
        # test machine. For now we fail on tests using multiple machines.
        print(f"Instanciating <{channel}/nixos/tests/{nix_path}> ({i+1}/{n_tests})")
        p = subprocess.run(
            [
                "nix-instantiate",
                f"<{channel}/nixos/tests/{nix_path}>",
                "-A",
                "driver.nodes.machine.config.environment.etc.systemd/system",
            ],
            capture_output=True,
        )
        if p.returncode != 0:
            print("Error while calling nix-instantiate")
            continue
        for drv_path in p.stdout.decode().split("\n")[:-1]:
            # Explore derivation outputs
            p = subprocess.run(
                [
                    "nix",
                    "--extra-experimental-features",
                    "nix-command",
                    "show-derivation",
                    "-r",
                    drv_path,
                ],
                capture_output=True,
            )
            if p.returncode != 0:
                print("Error while calling nix show-derivation")
                continue
            json_out = json.loads(p.stdout)
            for drv in json_out.values():
                path = drv.get("outputs", {}).get("out", {}).get("path")
                if path and drv_pattern.search(path):
                    unit_name = path.split("-unit-")[-1]
                    unit_name = unit_name.replace("-.service", "@.service")

                    if (
                        unit_name.startswith("acme-")
                        or "test.service" in unit_name
                        or unit_name.startswith("test")
                        or unit_name.startswith("network-addresses-")
                        or unit_name.startswith("vboxtestlog-")
                    ):
                        continue  # ignore

                    path = f"{path}/{unit_name}"
                    services_drv.add(path)

    return services_drv


def get_service_from_path(path) -> (str, str):
    """Return service name and content from path."""
    print(f"Fetching {path}")
    ret, out = subprocess.getstatusoutput(
        f"nix store cat --store https://cache.nixos.org/ {path} --extra-experimental-features nix-command"
    )
    if ret != 0:
        print("Error while fetching path")
        return "", ""
    service_name = path.split("/")[-1]

    # Remove NixOS specific from output
    out = re.sub(r"/nix/store/[A-Za-z\d\-\.]+/", "/usr/", out)
    out = re.sub(r"/nix/store/[a-z\d]+-", "", out)
    out = re.sub(
        r"Environment=\"(PATH|TZDIR|LOCALE_ARCHIVE|PYTHONPATH|LD_LIBRARY_PATH)=[^\"]*\"\n",
        "\n",
        out,
    )
    out = re.sub(r"X-[\w-]+=[^\n]+\n", "\n", out)

    return service_name, out
