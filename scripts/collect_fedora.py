#!/usr/bin/env python
# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

from utils.fedora_source import get_pkg_url_containing_services, get_services_from_pkg
from utils.service_json import update_service_json

mirror = "http://distrib-coffee.ipsl.jussieu.fr/pub/linux/fedora/linux/development"
dist = "rawhide"
arch = "x86_64"
for name, url in get_pkg_url_containing_services(mirror, dist, arch):
    for service_name, service_content in get_services_from_pkg(url):
        data_path = f"./data/service/{service_name}.json"
        source_name = f"https://packages.fedoraproject.org/pkgs/{name}/"
        update_service_json(data_path, source_name, service_content)
