#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from pathlib import Path
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_hyperv_vms_files(conf: Any) -> FileGenerator:
    if conf:
        yield Plugin(base_os=OS.WINDOWS, source=Path("hyperv_vms.ps1"))


register.bakery_plugin(
    name="hyperv_vms",
    files_function=get_hyperv_vms_files,
)
