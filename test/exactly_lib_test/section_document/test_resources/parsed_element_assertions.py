import pathlib
from typing import Sequence

from exactly_lib.section_document.parsed_section_element import ParsedSectionElement, ParsedFileInclusionDirective
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_file_inclusion_directive(expected: ValueAssertion[ParsedFileInclusionDirective]
                                ) -> ValueAssertion[ParsedSectionElement]:
    return asrt.is_instance_with(ParsedFileInclusionDirective, expected)


def matches_file_inclusion_directive(
        files_to_include: ValueAssertion[Sequence[pathlib.Path]] = asrt.anything_goes(),
        source: ValueAssertion[LineSequence] = asrt.anything_goes(),
) -> ValueAssertion[ParsedFileInclusionDirective]:
    return asrt.and_([
        asrt.sub_component('files_to_include',
                           ParsedFileInclusionDirective.files_to_include.fget,
                           files_to_include),
        asrt.sub_component('source',
                           ParsedFileInclusionDirective.source.fget,
                           source),
    ])
