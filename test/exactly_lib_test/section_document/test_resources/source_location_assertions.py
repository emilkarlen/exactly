import pathlib
from typing import Sequence, Optional, List

from exactly_lib.section_document.source_location import SourceLocation, SourceLocationPath, FileLocationInfo, \
    SourceLocationInfo
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


def matches_file_location_info(
        abs_path_of_dir_containing_root_file: asrt.ValueAssertion[pathlib.Path],
        file_path_rel_referrer: asrt.ValueAssertion[Optional[pathlib.Path]] = asrt.anything_goes(),
        file_inclusion_chain: asrt.ValueAssertion[Sequence[SourceLocation]] = asrt.anything_goes(),
        abs_path_of_dir_containing_file: asrt.ValueAssertion[Optional[pathlib.Path]] = asrt.anything_goes(),
) -> asrt.ValueAssertion[FileLocationInfo]:
    return asrt.is_instance_with_many(FileLocationInfo,
                                      [
                                          asrt.sub_component('abs_path_of_dir_containing_root_file',
                                                             FileLocationInfo.abs_path_of_dir_containing_root_file.fget,
                                                             abs_path_of_dir_containing_root_file),
                                          asrt.sub_component('file_path_rel_referrer',
                                                             FileLocationInfo.file_path_rel_referrer.fget,
                                                             file_path_rel_referrer),
                                          asrt.sub_component('file_inclusion_chain',
                                                             FileLocationInfo.file_inclusion_chain.fget,
                                                             file_inclusion_chain),
                                          asrt.sub_component('abs_path_of_dir_containing_file',
                                                             FileLocationInfo.abs_path_of_dir_containing_file.fget,
                                                             abs_path_of_dir_containing_file),
                                      ])


def matches_source_location_info(
        abs_path_of_dir_containing_root_file: asrt.ValueAssertion[pathlib.Path] = asrt.anything_goes(),
        source_location_path: asrt.ValueAssertion[SourceLocationPath] = asrt.anything_goes(),
        abs_path_of_dir_containing_file: asrt.ValueAssertion[Optional[pathlib.Path]] = asrt.anything_goes(),
) -> asrt.ValueAssertion[SourceLocationInfo]:
    return asrt.is_instance_with_many(
        SourceLocationInfo,
        [
            asrt.sub_component('abs_path_of_dir_containing_root_file',
                               SourceLocationInfo.abs_path_of_dir_containing_root_file.fget,
                               abs_path_of_dir_containing_root_file),
            asrt.sub_component('source_location_path',
                               SourceLocationInfo.source_location_path.fget,
                               source_location_path),
            asrt.sub_component('abs_path_of_dir_containing_file',
                               SourceLocationInfo.abs_path_of_dir_containing_file.fget,
                               abs_path_of_dir_containing_file),
        ])


def matches_source_location_info2(
        source: asrt.ValueAssertion[LineSequence] = asrt.anything_goes(),
        file_path_rel_referrer: asrt.ValueAssertion[pathlib.Path] = asrt.anything_goes(),
        file_inclusion_chain: asrt.ValueAssertion[Sequence[SourceLocation]] = asrt.anything_goes(),
        abs_path_of_dir_containing_file: asrt.ValueAssertion[pathlib.Path] = asrt.anything_goes(),
        abs_path_of_dir_containing_root_file: asrt.ValueAssertion[pathlib.Path] = asrt.anything_goes(),
) -> asrt.ValueAssertion[SourceLocationInfo]:
    return matches_source_location_info(
        abs_path_of_dir_containing_root_file=abs_path_of_dir_containing_root_file,
        abs_path_of_dir_containing_file=abs_path_of_dir_containing_file,
        source_location_path=matches_source_location_path(
            matches_source_location(source, file_path_rel_referrer),
            file_inclusion_chain))


def equals_file_inclusion_chain(expected: List[SourceLocation]
                                ) -> asrt.ValueAssertion[Sequence[SourceLocation]]:
    return asrt.matches_sequence([
        equals_source_location(sl)
        for sl in expected
    ])
