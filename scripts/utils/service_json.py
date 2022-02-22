# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

import json
import os

from .systemd_parser import SystemdUnitParser


def update_service_json(data_path, source_name, service_content):
    """Update service JSON using provided systemd unit."""
    # load or create database file for this service
    if os.path.isfile(data_path):
        print(f"Updating {data_path}")
        with open(data_path) as f:
            data = json.load(f)
    else:
        print(f"Creating {data_path}")
        data = {"provided_by": [], "unit": {}}

    # add source_name to provided_by
    if source_name not in data["provided_by"]:
        data["provided_by"].append(source_name)
        data["provided_by"].sort()

    # remove source from all options
    for section, options in data["unit"].items():
        for option, values in options.items():
            for value, sources in values.items():
                if source_name in sources:
                    data["unit"][section][option][value].remove(source_name)
                    data["unit"][section][option][value].sort()
            # remove values without sources
            data["unit"][section][option] = {
                v: s for v, s in data["unit"][section][option].items() if s
            }
        # remove options without values
        data["unit"][section] = {o: v for o, v in data["unit"][section].items() if v}
    # remove sections without options
    data["unit"] = {s: o for s, o in data["unit"].items() if o}

    # parse systemd unit
    config = SystemdUnitParser()
    try:
        config.read_string(service_content)
    except Exception as e:
        print(f"Failed to parse", e)
        return

    # add to local database
    for section in config.sections():
        if section not in data["unit"]:
            data["unit"][section] = {}
        for key, value in config.items(section):
            if type(value) == tuple:
                value = " ".join(value)
            value = value.strip()
            if value.lower() == "true":
                value = "yes"  # merge yes and true
            if value.lower() == "false":
                value = "no"  # merge no and false
            if key not in data["unit"][section]:
                # adding missing option
                data["unit"][section][key] = {}
            if value not in data["unit"][section][key]:
                # adding missing value
                data["unit"][section][key][value] = []
            if source_name not in data["unit"][section][key][value]:
                # add missing source_name
                data["unit"][section][key][value].append(source_name)
                data["unit"][section][key][value].sort()

    # save
    with open(data_path, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4)
