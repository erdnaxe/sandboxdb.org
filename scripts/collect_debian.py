#!/usr/bin/env python
# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

from utils.debian_source import (
    get_pkg_containing_services,
    get_pkgs_url,
    get_services_from_deb,
)
from utils.service_json import update_service_json

mirror = "https://mirrors.gandi.net/debian"
dist = "unstable"
for arch in ["all", "amd64"]:
    for component in ["main", "contrib"]:
        pkgs_names = get_pkg_containing_services(mirror, dist, component, arch)
        pkgs_names_urls = get_pkgs_url(pkgs_names, mirror, dist, component, arch)
        for name, url in pkgs_names_urls:
            for service_name, service_content in get_services_from_deb(url):
                data_path = f"./data/service/{service_name}.json"
                source_name = f"https://packages.debian.org/{dist}/{name}"
                update_service_json(data_path, source_name, service_content)
