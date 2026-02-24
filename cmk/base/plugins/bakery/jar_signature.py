#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Sequence
from pathlib import Path
from shlex import quote

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_jar_signature_files(conf: Sequence[str]) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("jar_signature"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=_get_jar_signature_config_lines(conf),
        target=Path("jar_signature.cfg"),
        include_header=True,
    )


def _get_jar_signature_config_lines(conf: Sequence[str]) -> list[str]:
    return [
        "JAVA_HOME=%s" % quote(conf[0]),
        "JAR_PATH=%s" % quote(" ".join(conf[1])),
    ]


register.bakery_plugin(
    name="jar_signature",
    files_function=get_jar_signature_files,
)
