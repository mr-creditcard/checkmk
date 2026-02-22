#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, override, Protocol, runtime_checkable, TypeVar

from cmk.rulesets.v1 import Label, Message, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    FormSpec,
    InputHint,
    InvalidElementValidator,
    List,
    MultipleChoiceElement,
)


class AutocompleterParams(Protocol):
    @property
    def show_independent_of_context(self) -> bool | None: ...
    @property
    def strict(self) -> bool | None: ...
    @property
    def escape_regex(self) -> bool | None: ...
    @property
    def world(self) -> str | None: ...
    @property
    def context(self) -> Mapping[str, Any] | None: ...
    @property
    def input_hint(self) -> str | None: ...


class AutocompleterData(Protocol):
    @property
    def ident(self) -> str: ...
    @property
    def params(self) -> AutocompleterParams: ...


class FetchMethod(Protocol):
    @property
    def value(self) -> str: ...


@runtime_checkable
class Autocompleter(Protocol):
    @property
    def data(self) -> AutocompleterData: ...
    @property
    def fetch_method(self) -> FetchMethod | None: ...


T = TypeVar("T")


@dataclass(frozen=True, kw_only=True)
class ListExtended[ModelT](List[ModelT]):
    prefill: DefaultValue[Sequence[ModelT]]


@dataclass(frozen=True, kw_only=True)
class SingleChoiceElementExtended(Generic[T]):
    name: T
    title: Title


@dataclass(frozen=True, kw_only=True)
class SingleChoiceExtended(Generic[T], FormSpec[T]):
    # SingleChoice:
    elements: (
        Sequence[SingleChoiceElementExtended[T]]
        | Callable[[], Sequence[SingleChoiceElementExtended[T]]]
    )
    no_elements_text: Message | None = None
    frozen: bool = False
    label: Label | None = None
    prefill: DefaultValue[T] | InputHint[Title] = InputHint(Title("Please choose"))
    ignored_elements: tuple[str, ...] = ()
    invalid_element_validation: InvalidElementValidator | None = None


@dataclass(frozen=True, kw_only=True)
class MultipleChoiceExtendedLayout(str, Enum):
    auto = "auto"
    dual_list = "dual_list"
    checkbox_list = "checkbox_list"


@dataclass(frozen=True, kw_only=True)
class MultipleChoiceElementExtended(MultipleChoiceElement):
    """Specifies an element of a multiple choice form.

    It can and should only be used internally when using it to generate MultipleChoiceExtended
    FormSpecs when the input data is not predefined, for example when creating FormSpecs based on
    user input, like for contact groups.
    """

    @override
    def __post_init__(self) -> None:
        pass


@dataclass(frozen=True, kw_only=True)
class MultipleChoiceExtended(FormSpec[Sequence[str]]):
    elements: Sequence[MultipleChoiceElement] | Autocompleter
    show_toggle_all: bool = False
    prefill: DefaultValue[Sequence[str]] = DefaultValue(())
    layout: MultipleChoiceExtendedLayout = MultipleChoiceExtendedLayout.auto

    def __post_init__(self) -> None:
        if not isinstance(self.elements, Autocompleter):
            available_names = {elem.name for elem in self.elements}
            if invalid := set(self.prefill.value) - available_names:
                raise ValueError(f"Invalid prefill element(s): {', '.join(invalid)}")
