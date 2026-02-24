#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_plesk_files(conf: int) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("plesk_backups.py"), interval=conf)
    yield Plugin(base_os=OS.LINUX, source=Path("plesk_domains.py"))


register.bakery_plugin(
    name="plesk",
    files_function=get_plesk_files,
)
