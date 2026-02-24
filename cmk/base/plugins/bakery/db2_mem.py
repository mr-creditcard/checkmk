#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_db2_mem_files(conf: bool) -> FileGenerator:
    for o_s in (OS.LINUX, OS.SOLARIS, OS.AIX):
        if conf:
            yield Plugin(base_os=o_s, source=Path("db2_mem"))


register.bakery_plugin(
    name="db2_mem",
    files_function=get_db2_mem_files,
)
