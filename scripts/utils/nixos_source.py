# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

import re
import subprocess


def get_services_store_path() -> [(str, str)]:
    """Return services files store paths.

    You need to have previously run: `nix-index -f "<nixos-unstable>"`
    """
    ret, out = subprocess.getstatusoutput(
        "nix-locate --at-root -r '/lib/systemd/.*\.service$'"
    )
    if ret != 0:
        print("Error while calling nix-locate")
        return []
    for line in out.split("\n"):
        line = line.split()
        name = line[0].split(".")[0].replace("(", "")
        file_type = line[-2]
        path = line[-1]
        if file_type == "r":
            yield name, path


def get_service_from_path(path) -> (str, str):
    """Return service name and content from path."""
    print(f"Fetching {path} from https://cache.nixos.org/")
    ret, out = subprocess.getstatusoutput(
        f"nix store cat --store https://cache.nixos.org/ {path} --extra-experimental-features nix-command"
    )
    if ret != 0:
        print(f"Error while parsing {path}")
        return "", ""
    service_name = path.split("/")[-1]

    # Remove store paths from output
    out = re.sub(r"/nix/store/[^/]+/", "/usr/", out)

    return service_name, out
