#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_mk_filehandler_files(conf: object) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("mk_filehandler"))


register.bakery_plugin(
    name="mk_filehandler",
    files_function=get_mk_filehandler_files,
)
