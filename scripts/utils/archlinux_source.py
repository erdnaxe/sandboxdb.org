# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

import io
import tarfile
import urllib.request
from tempfile import NamedTemporaryFile

import zstandard


def get_pkg_url_containing_services(
    mirror, repository="core", arch="x86_64"
) -> [(str, str)]:
    """Return package URLs containing services files."""
    with NamedTemporaryFile() as compressed_f:
        url = f"{mirror}/{repository}/os/{arch}/{repository}.files.tar.gz"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, compressed_f.name)
        f = tarfile.open(compressed_f.name)
        for member in f.getmembers():
            if not member.isdir():
                continue  # only consider directories

            # check if package contains service files
            files_file = f.extractfile(f"{member.name}/files")
            found = False
            for line in files_file.readlines():
                if b"lib/systemd/" in line and line.endswith(b".service\n"):
                    found = True
                    break
            if not found:
                continue
            files_file.close()

            # read package description
            desc_file = f.extractfile(f"{member.name}/desc")
            filename, name, section = "", "", ""
            for line in desc_file.readlines():
                if line == b"%FILENAME%\n":
                    section = "filename"
                elif line == b"%NAME%\n":
                    section = "name"
                elif section == "filename":
                    filename = line.decode().strip()
                    section = ""
                elif section == "name":
                    name = line.decode().strip()
                    section = ""
            desc_file.close()

            if repository == "community":
                url = f"{mirror}/pool/community/{filename}"
            else:
                url = f"{mirror}/pool/packages/{filename}"

            yield name, url


def get_services_from_pkg(url) -> (str, str):
    """Download and extract service files from ArchLinux package."""
    with NamedTemporaryFile() as compressed_f:
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, compressed_f.name)

        with zstandard.ZstdDecompressor().stream_reader(compressed_f) as zdata:
            try:
                tar = io.BytesIO(zdata.read())
            except zstandard.ZstdError:
                print("Error while decompressing zarchive")
                return tuple()
            with tarfile.open(fileobj=tar, mode="r:") as f:
                for path in f.getnames():
                    if "lib/systemd/" in path and path.endswith(".service"):
                        try:
                            service_file = io.TextIOWrapper(f.extractfile(path))
                        except KeyError:
                            continue  # broken symlink
                        service_name = path.split("/")[-1]
                        yield service_name, service_file.read()
