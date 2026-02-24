#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_mk_db2_files(conf: dict[str, int]) -> FileGenerator:
    for opsys in [OS.LINUX, OS.AIX]:
        yield Plugin(
            base_os=opsys,
            source=Path(f"mk_db2.{opsys}"),
            target=Path("mk_db2"),
            interval=conf.get("interval"),
        )


register.bakery_plugin(
    name="mk_db2",
    files_function=get_mk_db2_files,
)
