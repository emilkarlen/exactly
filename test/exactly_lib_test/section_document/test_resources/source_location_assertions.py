import pathlib
from typing import Sequence

from exactly_lib.section_document.source_location import SourceLocation, SourceLocationPath
from exactly_lib.util.line_source import LineSequence, Line
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence, matches_line_sequence


def matches_source_location(source: asrt.ValueAssertion[LineSequence] = asrt.anything_goes(),
                            file_path_rel_referrer: asrt.ValueAssertion[pathlib.Path] = asrt.anything_goes(),
                            ) -> asrt.ValueAssertion[SourceLocation]:
    return asrt.is_instance_with(SourceLocation,
                                 asrt.and_([
                                     asrt.sub_component('source',
                                                        SourceLocation.source.fget,
                                                        source),
                                     asrt.sub_component('file_path_rel_referrer',
                                                        SourceLocation.file_path_rel_referrer.fget,
                                                        file_path_rel_referrer),
                                 ]))


def equals_source_location(expected: SourceLocation) -> asrt.ValueAssertion[SourceLocation]:
    return matches_source_location(source=equals_line_sequence(expected.source),
                                   file_path_rel_referrer=asrt.equals(expected.file_path_rel_referrer))


def equals_source_location_sequence(expected: Sequence[SourceLocation]
                                    ) -> asrt.ValueAssertion[Sequence[SourceLocation]]:
    return asrt.matches_sequence(list(map(equals_source_location,
                                          expected)))


def matches_source_location_path(
        source_location: asrt.ValueAssertion[SourceLocation] = asrt.anything_goes(),
        file_inclusion_chain: asrt.ValueAssertion[Sequence[SourceLocation]] = asrt.anything_goes(),
) -> asrt.ValueAssertion[SourceLocationPath]:
    return asrt.is_instance_with(SourceLocationPath,
                                 asrt.and_([
                                     asrt.sub_component('location',
                                                        SourceLocationPath.location.fget,
                                                        source_location),
                                     asrt.sub_component('file_inclusion_chain',
                                                        SourceLocationPath.file_inclusion_chain.fget,
                                                        file_inclusion_chain),
                                 ]))


def equals_source_location_path(expected: SourceLocationPath) -> asrt.ValueAssertion[SourceLocationPath]:
    return matches_source_location_path(
        source_location=equals_source_location(expected.location),
        file_inclusion_chain=equals_source_location_sequence(expected.file_inclusion_chain))


def equals_single_line_source_location_path(expected: Line) -> asrt.ValueAssertion[SourceLocationPath]:
    return matches_source_location_path(
        source_location=matches_source_location(
            source=matches_line_sequence(
                first_line_number=asrt.equals(expected.line_number),
                lines=asrt.matches_sequence([asrt.equals(expected.text)])),
            file_path_rel_referrer=asrt.is_none),
        file_inclusion_chain=equals_source_location_sequence([]))
