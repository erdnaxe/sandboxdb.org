# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

import gzip
import io
import subprocess
import tarfile
import urllib.request
from tempfile import NamedTemporaryFile, TemporaryDirectory


def get_pkg_containing_services(
    mirror, dist="testing", component="main", arch="all"
) -> {str}:
    """Return package names containing services files."""
    pkgs = set()
    with NamedTemporaryFile() as compressed_f:
        url = f"{mirror}/dists/{dist}/{component}/Contents-{arch}.gz"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, compressed_f.name)
        with gzip.open(compressed_f) as f:
            for line in f.readlines():
                path, pkg = line.decode().strip().split(maxsplit=1)
                pkg = pkg.split("/")[-1]
                if pkg == "systemd-tests":
                    continue  # ignore
                if "lib/systemd/" in path and path.endswith(".service"):
                    pkgs.add(pkg)
    return pkgs


def get_pkgs_url(
    pkgs_name, mirror, dist="testing", component="main", arch="all"
) -> [(str, str)]:
    """Get distribution package name and URL for each package."""
    with NamedTemporaryFile() as compressed_f:
        url = f"{mirror}/dists/{dist}/{component}/binary-{arch}/Packages.gz"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, compressed_f.name)
        with gzip.open(compressed_f) as f:
            pkg = ""
            for line in f.readlines():
                if line.startswith(b"Package:"):
                    pkg = line.decode().strip().split(" ")[-1]
                    if pkg not in pkgs_name:
                        pkg = ""  # skip
                elif line.startswith(b"Filename:") and pkg:
                    path = line.decode().strip().split(" ")[-1]
                    yield pkg, f"{mirror}/{path}"
                    pkg = ""


def get_services_from_deb(url) -> [(str, io.TextIOWrapper)]:
    """Download and extract service files from Debian package."""
    with NamedTemporaryFile() as compressed_f:
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, compressed_f.name)

        with TemporaryDirectory() as d:
            ret, _ = subprocess.getstatusoutput(
                f"ar x {compressed_f.name} data.tar.xz --output {d}"
            )
            if ret != 0:
                print("Failed to extract Debian archive")
                return []

            try:
                f = tarfile.open(f"{d}/data.tar.xz")
            except FileNotFoundError:
                print("data.tar.xz was not found")
                return []

            for path in f.getnames():
                if "lib/systemd/" in path and path.endswith(".service"):
                    try:
                        service_file = io.TextIOWrapper(f.extractfile(path))
                    except KeyError:
                        continue  # broken symlink
                    service_name = path.split("/")[-1]
                    yield service_name, service_file.read()

            f.close()
