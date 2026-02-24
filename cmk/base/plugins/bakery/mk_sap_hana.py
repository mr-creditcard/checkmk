#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from .bakery_api.v1 import FileGenerator, OS, password_store, Plugin, PluginConfig, register

_UserAndPwd = tuple[str, password_store.PasswordId]


class _Conf(BaseModel):
    credentials: _UserAndPwd | str | list[tuple[str, str, str, _UserAndPwd | str]]
    credentials_sap_connect: _UserAndPwd | None = None
    runas: Literal["instance", "agent"] | None = None


def get_mk_sap_hana_files(conf: Mapping[str, object]) -> FileGenerator:
    config = _Conf.model_validate(conf)
    yield Plugin(base_os=OS.LINUX, source=Path("mk_sap_hana"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(_get_mk_sap_hana_config(config)),
        target=Path("sap_hana.cfg"),
        include_header=True,
    )


def _get_mk_sap_hana_config(config: _Conf) -> Iterator[str]:
    """
    >>> list(
    ...    _get_mk_sap_hana_config({"credentials": ("peter", ("password", "abc123"))})
    ... )  # doctest: +SKIP
    ['USER=peter', 'PASSWORD=abc123']
    >>> list(
    ...    _get_mk_sap_hana_config({"credentials": "storekey", "runas": "agent"})
    ... )  # doctest: +SKIP
    ['USERSTOREKEY=storekey', 'RUNAS=agent']
    >>> list(_get_mk_sap_hana_config({
    ...    "credentials": [
    ...        ("sid1", "inst1", "db1", ("usr1", ("password", "pw1"))),
    ...        ("sid2", "inst2", "db2", "storekey2"),
    ...    ],
    ...    "credentials_sap_connect": ("peter", ("password", "abc123"))
    ... }))  # doctest: +SKIP
    ['DBS=(sid1,inst1,db1,usr1,pw1, sid2,inst2,db2,,,storekey2)', 'USER_CONNECT=peter', 'PASSWORD_CONNECT=abc123']
    """
    match config.credentials:
        case list() as credentials:
            yield _get_sap_hana_databases(credentials)
        case str(credentials):
            yield f"USERSTOREKEY={credentials}"
        case credentials:
            yield from _user_and_pwd_lines(credentials)

    if (csc := config.credentials_sap_connect) is not None:
        yield from _user_and_pwd_lines(csc, suffix="_CONNECT")

    if config.runas:
        yield f"RUNAS={config.runas}"


def _user_and_pwd_lines(
    credentials: _UserAndPwd,
    *,
    suffix: Literal["", "_CONNECT"] = "",
) -> tuple[str, str]:
    user, indiv_or_stored_pwd = credentials
    pwd = password_store.extract(indiv_or_stored_pwd)
    return (f"USER{suffix}={user}", f"PASSWORD{suffix}={pwd}")


def _get_sap_hana_databases(db_conf: Iterable[tuple[str, str, str, _UserAndPwd | str]]) -> str:
    databases = []
    for sid, instance, db_name, credentials in db_conf:
        user = credentials[0] if isinstance(credentials, tuple) else ""
        password = password_store.extract(credentials[1]) if isinstance(credentials, tuple) else ""
        userstorekey = "" if isinstance(credentials, tuple) else credentials
        databases.append(f"{sid},{instance},{db_name},{user},{password},{userstorekey}")

    db_list = " ".join(databases)
    return f"DBS=({db_list})"


register.bakery_plugin(
    name="mk_sap_hana",
    files_function=get_mk_sap_hana_files,
)
