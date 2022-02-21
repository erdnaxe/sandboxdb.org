#!/usr/bin/env python
# Copyright (c) 2022 Alexandre Iooss <erdnaxe@crans.org>
# SPDX-License-Identifier: MIT

import glob
import os

for service in glob.glob("data/service/*.json"):
    name = service[:-5].split("/")[-1]
    content = f'---\ntitle: {name}\n---\n\n{{{{% provided_by "{name}" %}}}}\n\n## Options\n\n{{{{% systemd_unit "{name}" %}}}}\n\n## Additionnal notes\n\nNothing here.'
    hugo_name = name.replace("@", "-")
    path = f"content/service/{hugo_name}.md"
    if os.path.exists(path):
        continue
    with open(path, "w") as f:
        print("Creating", path)
        f.write(content)
