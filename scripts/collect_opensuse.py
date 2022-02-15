#!/usr/bin/env python
# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

from utils.opensuse_source import get_pkg_url_containing_services, get_services_from_pkg
from utils.service_json import update_service_json

mirror = "http://fr2.rpmfind.net/linux/opensuse"
dist = "tumbleweed"
for name, url in get_pkg_url_containing_services(mirror, dist):
    for service_name, service_content in get_services_from_pkg(url):
        data_path = f"./data/service/{service_name}.json"
        source_name = f"https://software.opensuse.org/package/{name}"
        update_service_json(data_path, source_name, service_content)
