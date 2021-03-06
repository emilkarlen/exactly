from pathlib import Path
from typing import Sequence, Optional

from exactly_lib.section_document.exceptions import FileSourceError, FileAccessError
from exactly_lib.section_document.source_location import SourceLocation
from exactly_lib.util.line_source import Line, line_sequence_from_line
from exactly_lib_test.section_document.test_resources.source_location_assertions import equals_source_location_sequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def is_file_source_error(expected: Assertion[FileSourceError]) -> Assertion[Exception]:
    return asrt.is_instance_with(FileSourceError, expected)


def matches_file_source_error(maybe_section_name: Assertion[str],
                              location_path: Sequence[SourceLocation]) -> Assertion[FileSourceError]:
    return asrt.and_([
        asrt.sub_component('maybe_section_name',
                           FileSourceError.maybe_section_name.fget,
                           maybe_section_name),
        asrt.sub_component('message',
                           FileSourceError.message.fget,
                           asrt.is_not_none),
        asrt.sub_component('location_path',
                           FileSourceError.location_path.fget,
                           equals_source_location_sequence(location_path)),
    ])


def file_source_error_equals_line(line: Line,
                                  maybe_section_name: Assertion[str] = asrt.anything_goes()
                                  ) -> Assertion[FileSourceError]:
    return asrt.and_([
        asrt.sub_component('maybe_section_name',
                           FileSourceError.maybe_section_name.fget,
                           maybe_section_name),
        asrt.sub_component('source',
                           FileSourceError.source.fget,
                           equals_line_sequence(line_sequence_from_line(line))),
    ])


def is_file_access_error(expected: Assertion[FileAccessError]) -> Assertion[Exception]:
    return asrt.is_instance_with(FileAccessError, expected)


def matches_file_access_error(erroneous_path: Path,
                              location_path: Sequence[SourceLocation],
                              section_name: Optional[str]) -> Assertion[FileAccessError]:
    return asrt.and_([
        asrt.sub_component('erroneous_path',
                           FileAccessError.erroneous_path.fget,
                           asrt.equals(erroneous_path)),
        asrt.sub_component('message',
                           FileAccessError.message.fget,
                           asrt.is_not_none),
        asrt.sub_component('location_path',
                           FileAccessError.location_path.fget,
                           equals_source_location_sequence(location_path)),
        asrt.sub_component('maybe_section_name',
                           FileAccessError.maybe_section_name.fget,
                           asrt.equals(section_name)),
    ])
