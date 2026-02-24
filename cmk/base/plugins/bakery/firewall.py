#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from .bakery_api.v1 import (
    register,
    WindowsConfigContent,
    WindowsConfigEntry,
    WindowsConfigGenerator,
)


def get_firewall_windows_config(conf: dict[str, WindowsConfigContent]) -> WindowsConfigGenerator:
    yield WindowsConfigEntry(path=["system", "firewall", "mode"], content=conf["mode"])
    yield WindowsConfigEntry(path=["system", "firewall", "port"], content=conf["port"])


register.bakery_plugin(
    name="firewall",
    windows_config_function=get_firewall_windows_config,
)
