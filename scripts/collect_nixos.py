#!/usr/bin/env python
# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

from utils.nixos_source import get_service_from_path, get_services_store_path
from utils.service_json import update_service_json

for name, path in get_services_store_path():
    service_name, service_content = get_service_from_path(path)
    if not service_name:
        continue

    data_path = f"./data/service/{service_name}.json"
    source_name = (
        f"https://search.nixos.org/packages?channel=unstable&show={name}&query={name}"
    )
    update_service_json(data_path, source_name, service_content)
