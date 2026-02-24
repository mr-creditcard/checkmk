#!/usr/bin/env python3
# Copyright (C) 2021 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Iterator
from pathlib import Path
from shlex import quote

from .bakery_api.v1 import FileGenerator, OS, PluginConfig, register


def get_python_plugins_files(conf: dict[str, str]) -> FileGenerator:
    if conf["version"] == "auto" and "command" not in conf:
        return

    for base_os in [OS.LINUX, OS.SOLARIS, OS.AIX]:
        yield PluginConfig(
            base_os=base_os,
            lines=list(_get_python_plugins_config(conf)),
            target=Path("python_path.cfg"),
            include_header=True,
        )


def _get_python_plugins_config(conf: dict[str, str]) -> Iterator[str]:
    command = conf.get("command")
    version = conf["version"]

    if command and version in ("python2", "auto"):
        yield f"PYTHON2={quote(command)}"

    if command and version in ("python3", "auto"):
        yield f"PYTHON3={quote(command)}"

    if version == "python2":
        yield "PYTHON3="

    if version == "python3":
        yield "PYTHON2="


register.bakery_plugin(
    name="python_plugins",
    files_function=get_python_plugins_files,
)
