#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from typing import Any

from .bakery_api.v1 import register, WindowsConfigGenerator, WindowsGlobalConfigEntry


def get_remove_legacy_windows_config(conf: Any) -> WindowsConfigGenerator:
    if conf:
        yield WindowsGlobalConfigEntry(name="remove_legacy", content="yes")


register.bakery_plugin(
    name="remove_legacy",
    windows_config_function=get_remove_legacy_windows_config,
)
