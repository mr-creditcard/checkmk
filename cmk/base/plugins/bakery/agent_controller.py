#!/usr/bin/env python3
# Copyright (C) 2022 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Mapping
from typing import Any

from .bakery_api.v1 import register, WindowsConfigEntry, WindowsConfigGenerator


def _path_to(entry: str) -> list[str]:
    return ["system", "controller", entry]


def get_agent_controller_windows_config(conf: Mapping[str, Any]) -> WindowsConfigGenerator:
    enabled, runtime_opts = conf.get("agent_ctl_enabled", (True, {}))
    yield WindowsConfigEntry(path=_path_to("run"), content=enabled)
    if enabled:
        yield from (
            WindowsConfigEntry(path=_path_to(runtime_opt), content=value)
            for runtime_opt, value in runtime_opts.items()
        )


register.bakery_plugin(
    name="agent_controller",
    windows_config_function=get_agent_controller_windows_config,
)
