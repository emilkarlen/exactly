import pathlib
from typing import Sequence, Optional, List

from exactly_lib.section_document.source_location import SourceLocation, SourceLocationPath, FileLocationInfo, \
    SourceLocationInfo
from exactly_lib.util.line_source import LineSequence, Line
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence, matches_line_sequence, \
    is_line_sequence


def matches_source_location(source: ValueAssertion[LineSequence] = asrt.anything_goes(),
                            file_path_rel_referrer: ValueAssertion[Optional[pathlib.Path]] = asrt.anything_goes(),
                            ) -> ValueAssertion[SourceLocation]:
    return asrt.is_instance_with(
        SourceLocation,
        asrt.and_([
            asrt.sub_component(
                'source',
                SourceLocation.source.fget,
                asrt.is_instance_with(LineSequence, source)),
            asrt.sub_component(
                'file_path_rel_referrer',
                SourceLocation.file_path_rel_referrer.fget,
                asrt.is_optional_instance_with(pathlib.Path, file_path_rel_referrer)),
        ]))


def equals_source_location(expected: SourceLocation) -> ValueAssertion[SourceLocation]:
    return matches_source_location(source=equals_line_sequence(expected.source),
                                   file_path_rel_referrer=asrt.equals(expected.file_path_rel_referrer))


def equals_source_location_sequence(expected: Sequence[SourceLocation]
                                    ) -> ValueAssertion[Sequence[SourceLocation]]:
    return asrt.matches_sequence(list(map(equals_source_location,
                                          expected)))


def matches_source_location_path(
        source_location: ValueAssertion[SourceLocation] = asrt.anything_goes(),
        file_inclusion_chain: ValueAssertion[Sequence[SourceLocation]] = asrt.anything_goes(),
) -> ValueAssertion[SourceLocationPath]:
    return asrt.is_instance_with(
        SourceLocationPath,
        asrt.and_([
            asrt.sub_component('location',
                               SourceLocationPath.location.fget,
                               asrt.is_instance_with(SourceLocation, source_location),
                               ),
            asrt.sub_component('file_inclusion_chain',
                               SourceLocationPath.file_inclusion_chain.fget,
                               asrt.and_([
                                   asrt.is_sequence_of(asrt.is_instance(SourceLocation)),
                                   file_inclusion_chain,
                               ]),
                               )
        ]))


def equals_source_location_path(expected: SourceLocationPath) -> ValueAssertion[SourceLocationPath]:
    return matches_source_location_path(
        source_location=equals_source_location(expected.location),
        file_inclusion_chain=equals_source_location_sequence(expected.file_inclusion_chain))


def equals_single_line_source_location_path(expected: Line) -> ValueAssertion[SourceLocationPath]:
    return matches_source_location_path(
        source_location=matches_source_location(
            source=matches_line_sequence(
                first_line_number=asrt.equals(expected.line_number),
                lines=asrt.matches_sequence([asrt.equals(expected.text)])),
            file_path_rel_referrer=asrt.is_none),
        file_inclusion_chain=equals_source_location_sequence([]))


def matches_file_location_info(
        abs_path_of_dir_containing_first_file_path: ValueAssertion[pathlib.Path] = asrt.anything_goes(),
        file_path_rel_referrer: ValueAssertion[Optional[pathlib.Path]] = asrt.anything_goes(),
        file_inclusion_chain: ValueAssertion[Sequence[SourceLocation]] = asrt.anything_goes(),
) -> ValueAssertion[FileLocationInfo]:
    return asrt.is_instance_with__many(
        FileLocationInfo,
        [
            asrt.sub_component('abs_path_of_dir_containing_first_file_path',
                               FileLocationInfo.abs_path_of_dir_containing_first_file_path.fget,
                               abs_path_of_dir_containing_first_file_path),
            asrt.sub_component('file_path_rel_referrer',
                               FileLocationInfo.file_path_rel_referrer.fget,
                               file_path_rel_referrer),
            asrt.sub_component('file_inclusion_chain',
                               FileLocationInfo.file_inclusion_chain.fget,
                               file_inclusion_chain),
        ])


def matches_source_location_info(
        abs_path_of_dir_containing_first_file_path: ValueAssertion[pathlib.Path] = asrt.anything_goes(),
        source_location_path: ValueAssertion[SourceLocationPath] = asrt.anything_goes(),
) -> ValueAssertion[SourceLocationInfo]:
    return asrt.is_instance_with__many(
        SourceLocationInfo,
        [
            asrt.sub_component('abs_path_of_dir_containing_first_file_path',
                               SourceLocationInfo.abs_path_of_dir_containing_first_file_path.fget,
                               asrt.is_instance_with(pathlib.Path,
                                                     abs_path_of_dir_containing_first_file_path)
                               ),
            asrt.sub_component('source_location_path',
                               SourceLocationInfo.source_location_path.fget,
                               asrt.is_instance_with(SourceLocationPath,
                                                     source_location_path),
                               ),
        ])


def is_valid_source_location_info() -> ValueAssertion[SourceLocationInfo]:
    is_valid_source_location = matches_source_location(
        source=is_line_sequence()
    )
    return matches_source_location_info(
        source_location_path=matches_source_location_path(
            source_location=is_valid_source_location,
            file_inclusion_chain=asrt.is_sequence_of(is_valid_source_location)
        )
    )


def equals_source_location_info(expected: SourceLocationInfo,
                                ) -> ValueAssertion[SourceLocationInfo]:
    return matches_source_location_info(
        abs_path_of_dir_containing_first_file_path=asrt.equals(expected.abs_path_of_dir_containing_first_file_path),
        source_location_path=equals_source_location_path(expected.source_location_path)
    )


def matches_source_location_info2(
        source: ValueAssertion[LineSequence] = asrt.anything_goes(),
        file_path_rel_referrer: ValueAssertion[pathlib.Path] = asrt.anything_goes(),
        file_inclusion_chain: ValueAssertion[Sequence[SourceLocation]] = asrt.anything_goes(),
        abs_path_of_dir_containing_root_file: ValueAssertion[pathlib.Path] = asrt.anything_goes(),
) -> ValueAssertion[SourceLocationInfo]:
    return matches_source_location_info(
        abs_path_of_dir_containing_first_file_path=abs_path_of_dir_containing_root_file,
        source_location_path=matches_source_location_path(
            matches_source_location(source, file_path_rel_referrer),
            file_inclusion_chain))


def equals_file_inclusion_chain(expected: List[SourceLocation]
                                ) -> ValueAssertion[Sequence[SourceLocation]]:
    return asrt.matches_sequence([
        equals_source_location(sl)
        for sl in expected
    ])
