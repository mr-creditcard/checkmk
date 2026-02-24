#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterable
from pathlib import Path

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_ibm_mq_files(conf: dict[str, Iterable[str]]) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("ibm_mq"))

    if not conf:
        return

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(_get_ibm_mq_config(conf)),
        target=Path("ibm_mq.cfg"),
        include_header=True,
    )


def _get_ibm_mq_config(queue_settings: dict[str, Iterable[str]]) -> Iterable[str]:
    only_qm = queue_settings.get("only_qm")
    if only_qm:
        yield "ONLY_QM=%s\n" % " ".join(only_qm)
    skip_qm = queue_settings.get("skip_qm")
    if skip_qm:
        yield "SKIP_QM=%s\n" % " ".join(skip_qm)

    another_user = queue_settings.get("execute_as_another_user")
    if another_user == "mqm":
        yield "EXEC_USER=MQM"


register.bakery_plugin(
    name="ibm_mq",
    files_function=get_ibm_mq_files,
)
