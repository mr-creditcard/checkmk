#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="possibly-undefined"

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_mk_postgres_files(conf: dict[str, Any]) -> FileGenerator:
    for current_os in (OS.LINUX, OS.WINDOWS):
        yield Plugin(base_os=current_os, source=Path("mk_postgres.py"))

        try:
            instances_settings = conf["instances_settings"]
        except (TypeError, KeyError):
            continue

        yield PluginConfig(
            base_os=current_os,
            lines=list(_get_mk_postgres_config(instances_settings, current_os)),
            target=Path("postgres.cfg"),
            include_header=True,
        )


def _get_mk_postgres_config(instances_settings: dict[str, Any], os: OS) -> Iterable[str]:
    if os == OS.LINUX:
        sep = ":"
    if os == OS.WINDOWS:
        sep = "|"

    yield "# Credentials for postgres instances"
    yield "DBUSER=%s" % instances_settings["db_username"]
    pg_binary_path = instances_settings.get("pg_binary_path")
    if pg_binary_path is not None:
        yield f"PG_BINARY_PATH={pg_binary_path}"
    for instance in instances_settings["instances"]:
        yield "INSTANCE={env}{sep}{un}{sep}{pg}{sep}{name}".format(
            env=instance["instance_env_filepath"],
            sep=sep,
            un=instance["instance_username"],
            pg=instance["instance_pgpass_filepath"],
            name=instance["instance_name"],
        )


register.bakery_plugin(
    name="mk_postgres",
    files_function=get_mk_postgres_files,
)
