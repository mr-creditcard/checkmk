#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path
from typing import assert_never, Literal

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_smart_files(conf: Literal["smart_posix", "smart"]) -> FileGenerator:
    match conf:
        case "smart_posix":
            yield Plugin(base_os=OS.LINUX, source=Path("smart_posix"))
        case "smart":
            yield Plugin(base_os=OS.LINUX, source=Path("smart"))
        case _:
            assert_never(conf)


register.bakery_plugin(
    name="smart",
    files_function=get_smart_files,
)
