#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Iterable
from pathlib import Path
from typing import TypedDict

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register

Auth = str | tuple[str, tuple[str, str]]
Excludes = list[str]


class Conf(TypedDict, total=False):
    auth_default: Auth
    auth_instances: list[tuple[str, Auth]]
    inst_excludes: Excludes
    timeout_connection: int
    timeout_command: int


def get_mssql_files(conf: Conf) -> FileGenerator:
    yield Plugin(base_os=OS.WINDOWS, source=Path("mssql.vbs"))

    auth = conf.get("auth_default", "system")
    yield PluginConfig(
        base_os=OS.WINDOWS,
        lines=list(
            _get_mssql_ini_lines(
                auth,
                conf,
                excludes=conf.get("inst_excludes"),
            ),
        ),
        target=Path("mssql.ini"),
    )

    for instance, auth_conf in conf.get("auth_instances", []):
        sane_id = _sanitize_instance_for_filename(instance)
        yield PluginConfig(
            base_os=OS.WINDOWS,
            lines=list(
                _get_mssql_ini_lines(
                    auth_conf,
                    conf,
                ),
            ),
            target=Path(f"mssql_{sane_id}.ini"),
        )


def _get_mssql_ini_lines(
    auth: Auth,
    conf: Conf,
    excludes: Excludes | None = None,
) -> Iterable[str]:
    yield "[auth]"
    if auth == "system":
        yield "type = system"
    else:
        assert isinstance(auth, tuple)
        yield "type = db"
        yield "username = %s" % auth[1][0]
        yield "password = %s" % auth[1][1]

    if excludes:
        yield "[instance]"
        yield "exclude = %s" % ",".join(excludes)

    yield "[timeouts]"
    if "timeout_connection" in conf:
        yield f"timeout_connection = {conf['timeout_connection']}"
    if "timeout_command" in conf:
        yield f"timeout_command = {conf['timeout_command']}"


def _sanitize_instance_for_filename(instance: str) -> str:
    # we can't have backslashes. Make sure this function
    # is mirrored in mssql.vbs!
    return instance.replace("\\", "_").replace(",", "_")


register.bakery_plugin(
    name="mssql",
    files_function=get_mssql_files,
)
