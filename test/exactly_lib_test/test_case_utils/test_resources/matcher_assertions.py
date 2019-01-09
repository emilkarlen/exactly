from typing import Optional, Sequence

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def arbitrary_validation_failure() -> ValueAssertion[Optional[str]]:
    return asrt.is_instance(str)


def matches_validation_failure(message: ValueAssertion[str]) -> ValueAssertion[Optional[str]]:
    return asrt.is_instance(str)


def arbitrary_matching_failure() -> ValueAssertion[Optional[str]]:
    return asrt.is_instance(str)


def is_matching_success() -> Optional[ValueAssertion[Optional[str]]]:
    return None


def is_hard_error() -> Optional[ValueAssertion[str]]:
    return asrt.is_instance(str)


class Expectation:
    def __init__(
            self,
            validation_post_sds: ValueAssertion[Optional[str]] = asrt.is_none,

            validation_pre_sds: ValueAssertion[Optional[str]] = asrt.is_none,

            main_result: Optional[ValueAssertion[Optional[str]]] = None,
            is_hard_error: Optional[ValueAssertion[str]] = None,
            symbol_usages: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
            main_side_effects_on_sds: ValueAssertion[SandboxDirectoryStructure] = asrt.anything_goes(),
            main_side_effects_on_home_and_sds: ValueAssertion[HomeAndSds] = asrt.anything_goes(),
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
    ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.is_hard_error = is_hard_error
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_home_and_sds = main_side_effects_on_home_and_sds
        self.source = source
        self.symbol_usages = symbol_usages


is_pass = Expectation
