#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_mk_docker_files(conf: dict[str, Any]) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("mk_docker.py"), interval=conf.get("interval"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(_get_mk_docker_config(conf)),
        target=Path("docker.cfg"),
        include_header=True,
    )


def _get_mk_docker_config(conf: dict[str, Any]) -> Iterable[str]:
    yield "[DOCKER]"
    # beware of the inverting in the Transfom of the WATO rule!
    skip_sections = conf.get("node", []) + conf.get("containers", [])
    if skip_sections:
        yield "skip_sections: %s" % ",".join(skip_sections)
    else:
        yield "# skip_sections: no sections skipped"

    yield "container_id: %s" % conf.get("container_id", "short")

    if "base_url" in conf:
        yield "base_url: %s" % conf["base_url"]

    if (persist_period_node_disk_usage := conf.get("persist_period_node_disk_usage")) is not None:
        yield f"persist_period_node_disk_usage: {persist_period_node_disk_usage}"


register.bakery_plugin(
    name="mk_docker",
    files_function=get_mk_docker_files,
)
