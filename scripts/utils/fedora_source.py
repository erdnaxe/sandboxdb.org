# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

import gzip
import io
import urllib.request
import xml.etree.ElementTree as ET
from tempfile import NamedTemporaryFile

import rpmfile


def get_pkg_url_containing_services(
    mirror, dist="rawhide", arch="x86_64"
) -> [(str, str)]:
    """Return package URLs containing services files."""
    # Get location of primary and filelists metadata
    with NamedTemporaryFile() as f:
        url = f"{mirror}/{dist}/Everything/{arch}/os/repodata/repomd.xml"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, f.name)
        root = ET.parse(f).getroot()
        primary_location = root.find(
            "./*[@type='primary']/{http://linux.duke.edu/metadata/repo}location"
        ).get("href")
        filelists_location = root.find(
            "./*[@type='filelists']/{http://linux.duke.edu/metadata/repo}location"
        ).get("href")

    # Collect package name mapping from primary metadata
    name_mapping = {}
    with NamedTemporaryFile() as compressed_f:
        url = f"{mirror}/{dist}/Everything/{arch}/os/{primary_location}"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, compressed_f.name)
        with gzip.open(compressed_f) as f:
            root = ET.parse(f).getroot()
            pkgs = root.findall("./{http://linux.duke.edu/metadata/common}package")
            for pkg in pkgs:
                name = pkg.find("./{http://linux.duke.edu/metadata/common}name").text
                sourcerpm = pkg.find(".//{http://linux.duke.edu/metadata/rpm}sourcerpm")
                if sourcerpm is not None:
                    sourcename = sourcerpm.text.rsplit("-", 2)[0]
                    if name != sourcename:
                        name_mapping[name] = f"{sourcename}/{name}"

    # Search service files in package filelists
    with NamedTemporaryFile() as compressed_f:
        url = f"{mirror}/{dist}/Everything/{arch}/os/{filelists_location}"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, compressed_f.name)
        with gzip.open(compressed_f) as f:
            root = ET.parse(f).getroot()
            pkgs = root.findall("./{http://linux.duke.edu/metadata/filelists}package")
            for pkg in pkgs:
                # check if package contains service files
                found = False
                paths = [
                    f.text
                    for f in pkg.findall(
                        "./{http://linux.duke.edu/metadata/filelists}file"
                    )
                ]
                for path in paths:
                    if "lib/systemd/" in path and path.endswith(".service"):
                        found = True
                if not found:
                    continue  # no service file

                # read package description
                name = pkg.get("name")
                parch = pkg.get("arch")
                version = pkg.find(
                    "./{http://linux.duke.edu/metadata/filelists}version"
                )
                ver = version.get("ver")
                rel = version.get("rel")
                first = name[0].lower()
                url = f"{mirror}/{dist}/Everything/{arch}/os/Packages/{first}/{name}-{ver}-{rel}.{parch}.rpm"

                if name == "systemd-tests":
                    continue  # ignore

                if name in name_mapping:
                    name = name_mapping[name]
                yield name, url


def get_services_from_pkg(url) -> [(str, bytes)]:
    """Download and extract service files from RPM package."""
    with NamedTemporaryFile() as compressed_f:
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, compressed_f.name)

        try:
            f = rpmfile.open(compressed_f.name)
        except AssertionError:
            print("Failed to extract RPM")
            return tuple()
        for member in f.getmembers():
            path = member.name
            if "lib/systemd/" in path and path.endswith(".service"):
                try:
                    service_content = f.extractfile(path).read().decode()
                except KeyError:
                    continue  # broken symlink
                service_name = path.split("/")[-1]
                yield service_name, service_content
