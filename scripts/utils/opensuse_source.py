# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

import gzip
import io
from urllib.request import urlopen, urlretrieve
import xml.etree.ElementTree as ET
from tempfile import NamedTemporaryFile

import rpmfile


def get_pkg_url_containing_services(mirror, dist="tumbleweed") -> [(str, str)]:
    """Return package URLs containing services files."""
    # Get location of primary and filelists metadata
    url = f"{mirror}/{dist}/repo/oss/repodata/repomd.xml"
    print(f"Downloading {url}")
    with urlopen(url) as f:
        root = ET.parse(f).getroot()
        primary_location = root.find(
            "./*[@type='primary']/{http://linux.duke.edu/metadata/repo}location"
        ).get("href")
        filelists_location = root.find(
            "./*[@type='filelists']/{http://linux.duke.edu/metadata/repo}location"
        ).get("href")

    # Search service files in package filelists
    url = f"{mirror}/{dist}/repo/oss/{filelists_location}"
    print(f"Downloading {url}")
    with urlopen(url) as compressed_f:
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
                url = f"{mirror}/{dist}/repo/oss/{parch}/{name}-{ver}-{rel}.{parch}.rpm"

                if name == "systemd-tests" or name == "systemd-testsuite":
                    continue  # ignore

                yield name, url


def get_services_from_pkg(url) -> [(str, bytes)]:
    """Download and extract service files from RPM package."""
    with NamedTemporaryFile() as compressed_f:
        print(f"Downloading {url}")
        urlretrieve(url, compressed_f.name)

        try:
            f = rpmfile.open(compressed_f.name)
        except AssertionError:
            print("Failed to extract RPM")
            return tuple()
        try:
            members = f.getmembers()
        except gzip.BadGzipFile as e:
            print("Failed to read RPM")
            return tuple()
        for member in members:
            path = member.name
            if "lib/systemd/" in path and path.endswith(".service"):
                try:
                    service_content = f.extractfile(path).read()
                except KeyError:
                    continue  # broken symlink
                service_name = path.split("/")[-1]
                yield service_name, service_content.decode()
