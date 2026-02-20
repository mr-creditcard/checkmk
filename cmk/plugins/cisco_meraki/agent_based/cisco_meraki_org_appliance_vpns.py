#!/usr/bin/env python3
# Copyright (C) 2025 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
#
# Original author: thl-cmk[at]outlook[dot]com

import dataclasses
import json
from collections.abc import Mapping
from typing import Self, TypedDict

from pydantic import BaseModel, Field

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
)

type Section = Mapping[str, Peer]


class Uplink(BaseModel, frozen=True):
    interface: str
    public_ip: str = Field(alias="publicIp")


class MerakiVpnPeer(BaseModel, frozen=True):
    network_name: str = Field(alias="networkName")
    reachability: str


class ThirdPartyVpnPeer(BaseModel, frozen=True):
    name: str
    public_ip: str = Field(alias="publicIp")
    reachability: str


@dataclasses.dataclass
class Peer:
    type: str
    vpn_mode: str
    uplinks: list[Uplink]
    reachability: str | None = None
    public_ip: str | None = None

    @classmethod
    def from_meraki(cls, peer: MerakiVpnPeer, vpn_mode: str, uplinks: list[Uplink]) -> Self:
        return cls(
            type="Meraki VPN peer",
            vpn_mode=vpn_mode,
            uplinks=uplinks,
            reachability=peer.reachability,
        )

    @classmethod
    def from_third_party(
        cls, peer: ThirdPartyVpnPeer, vpn_mode: str, uplinks: list[Uplink]
    ) -> Self:
        return cls(
            type="Third party VPN peer",
            vpn_mode=vpn_mode,
            uplinks=uplinks,
            public_ip=peer.public_ip,
            reachability=peer.reachability,
        )

    @property
    def status_reachable(self) -> bool:
        if not self.reachability:
            return False
        return self.reachability.lower() == "reachable"


class VpnStatus(BaseModel, frozen=True):
    meraki_vpn_peers: list[MerakiVpnPeer] = Field(alias="merakiVpnPeers")
    network_name: str = Field(alias="networkName")
    third_party_vpn_peers: list[ThirdPartyVpnPeer] = Field(alias="thirdPartyVpnPeers")
    uplinks: list[Uplink]
    vpn_mode: str = Field(alias="vpnMode")

    def get_peers_by_name(self) -> Section:
        return {
            **{
                peer.network_name: Peer.from_meraki(peer, self.vpn_mode, self.uplinks)
                for peer in self.meraki_vpn_peers
            },
            **{
                peer.name: Peer.from_third_party(peer, self.vpn_mode, self.uplinks)
                for peer in self.third_party_vpn_peers
            },
        }


def parse_appliance_vpns(string_table: StringTable) -> Section:
    match string_table:
        case [[payload]] if payload:
            vpn_status = VpnStatus.model_validate(json.loads(payload)[0])
            return vpn_status.get_peers_by_name()
        case _:
            return {}


agent_section_cisco_meraki_org_appliance_vpns = AgentSection(
    name="cisco_meraki_org_appliance_vpns",
    parse_function=parse_appliance_vpns,
)


def discover_appliance_vpns(section: Section) -> DiscoveryResult:
    for key in section:
        yield Service(item=key)


class CheckParams(TypedDict):
    status_not_reachable: int


def check_appliance_vpns(item: str, params: CheckParams, section: Section) -> CheckResult:
    if (peer := section.get(item)) is None:
        return None

    if peer.status_reachable:
        yield Result(state=State.OK, summary=f"Status: {peer.reachability}")
    else:
        yield Result(
            state=State(params["status_not_reachable"]),
            summary=f"Status: {peer.reachability}",
        )

    yield Result(state=State.OK, summary=f"Type: {peer.type}")
    if peer.public_ip:
        yield Result(state=State.OK, summary=f"Peer IP: {peer.public_ip}")

    yield Result(state=State.OK, notice=f"VPN mode: {peer.vpn_mode}")
    yield Result(state=State.OK, notice="Uplink(s):")
    for uplink in peer.uplinks:
        yield Result(
            state=State.OK, notice=f"Name: {uplink.interface}, Public IP: {uplink.public_ip}"
        )


check_plugin_cisco_meraki_org_appliance_vpns = CheckPlugin(
    name="cisco_meraki_org_appliance_vpns",
    service_name="VPN peer %s",
    discovery_function=discover_appliance_vpns,
    check_function=check_appliance_vpns,
    check_ruleset_name="cisco_meraki_org_appliance_vpns",
    check_default_parameters=CheckParams(status_not_reachable=State.WARN.value),
)
