#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
import configparser
import io
from pathlib import Path
from typing import assert_never, Literal, NotRequired, TypedDict

from .bakery_api.v1 import FileGenerator, OS, password_store, Plugin, PluginConfig, register

_CertKeyChoices = Literal["cert_filepath", "uploaded_cert_file"]
_CertChoices = tuple[_CertKeyChoices, str]


class ValuespecTlsResult(TypedDict):
    insecure: bool
    ca_file: NotRequired[str]
    cert_key_file: NotRequired[_CertChoices]


class _ValuespecResult(TypedDict):
    auth_mechanism: Literal[
        "DEFAULT",
        "MONGODB-CR",
        "SCRAM-SHA-256",
        "SCRAM-SHA-1",
        "MONGODB-X509",
    ]
    auth_source: str
    username: str
    password: password_store.PasswordId | str
    tls: NotRequired[ValuespecTlsResult]
    host: NotRequired[str]
    port: NotRequired[int]


class MongoDBConfigParser(configparser.ConfigParser):
    def __init__(self) -> None:
        super().__init__()
        self["MONGODB"] = {}

    def get_lines(self) -> list[str]:
        buffer = io.StringIO()
        self.write(buffer)
        return buffer.getvalue().rstrip().split("\n")


def _update_parser_with_cert(
    parser: MongoDBConfigParser, opt_name: _CertKeyChoices, value: str
) -> FileGenerator:
    match opt_name:
        case "cert_filepath":
            parser["MONGODB"]["tls_cert_key_file"] = value
        case "uploaded_cert_file":
            parser["MONGODB"]["tls_cert_key_file"] = "/etc/check_mk/mk_mongodb.pem"
            yield PluginConfig(
                base_os=OS.LINUX,
                lines=[value],
                target=Path("mk_mongodb.pem"),
            )
        case _:
            assert_never(opt_name)


def get_mk_mongodb_files(conf: Literal[True] | _ValuespecResult | None) -> FileGenerator:
    if conf is None:
        return

    yield Plugin(base_os=OS.LINUX, source=Path("mk_mongodb.py"))

    parser = make_config_parser(conf)

    if not isinstance(conf, bool) and (cert_cfg := conf.get("tls", {}).get("cert_key_file")):
        yield from _update_parser_with_cert(parser, *cert_cfg)

    yield PluginConfig(
        base_os=OS.LINUX,
        lines=parser.get_lines(),
        target=Path("mk_mongodb.cfg"),
        include_header=True,
    )


def make_config_parser(conf: Literal[True] | _ValuespecResult) -> MongoDBConfigParser:
    """Generate the lines of an INI-style configuration file

    Args:
        conf:
            The config, as defined by the ruleset.

    Returns:
        The config as a list of strings.

    """
    # See: enterprise/cmk/gui/cee/plugins/wato/agent_bakery/rulespecs/mk_mongodb.py
    parser = MongoDBConfigParser()
    if conf is True:
        return parser

    parser["MONGODB"] = {
        "username": conf["username"],
        "password": password_store.extract(conf["password"]),
        "auth_source": conf["auth_source"],
        "auth_mechanism": conf["auth_mechanism"],
    }
    if "host" in conf:
        parser["MONGODB"]["host"] = conf["host"]
    if "port" in conf:
        parser["MONGODB"]["port"] = str(conf["port"])

    if "tls" in conf:
        parser["MONGODB"].update(
            {
                "tls_enable": "true",
                "tls_verify": str(not conf["tls"]["insecure"]).lower(),
            }
        )
        if conf["tls"].get("ca_file"):
            parser["MONGODB"]["tls_ca_file"] = conf["tls"]["ca_file"]

    return parser


register.bakery_plugin(
    name="mk_mongodb",
    files_function=get_mk_mongodb_files,
)
