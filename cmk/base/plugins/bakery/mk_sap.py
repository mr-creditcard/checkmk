#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# mypy: disable-error-code="no-untyped-call"
# mypy: disable-error-code="no-untyped-def"

from pathlib import Path
from pprint import pformat
from typing import Any

from .bakery_api.v1 import FileGenerator, OS, password_store, Plugin, PluginConfig, register


def get_mk_sap_files(conf: Any) -> FileGenerator:
    yield Plugin(base_os=OS.LINUX, source=Path("mk_sap.py"))

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=list(_get_mk_sap_config(conf)),
        target=Path("sap.cfg"),
        include_header=True,
    )


def _get_mk_sap_config(conf):
    yield "# Instances to monitor"
    cfgs = []
    for instance in conf["instances"]:
        c = dict(instance.items())
        # Extract password if it's in tuple format (from MigrateToIndividualOrStoredPassword)
        if "passwd" in c:
            c["passwd"] = password_store.extract(c["passwd"])
        c["loglevel"] = "warn"  # hard coded. Other values currently unknown
        cfgs.append(c)
    yield from f"cfg = {pformat(cfgs)}".split("\n")
    yield ""
    yield ""
    yield "# CCMS paths to monitor"
    yield from f"monitor_paths += {pformat(conf['paths'], width=120)}".split("\n")


register.bakery_plugin(
    name="mk_sap",
    files_function=get_mk_sap_files,
)
