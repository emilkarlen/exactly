import pathlib
from typing import Optional

from exactly_lib.section_document.exceptions import ParseError
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_suite.file_reading.exception import SuiteParseError
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches_suite_parse_error(
        suite_file: Assertion[pathlib.Path] = asrt.anything_goes(),
        maybe_section_name: Assertion[Optional[str]] = asrt.anything_goes(),
        source: Assertion[Optional[LineSequence]] = asrt.anything_goes(),
        source_location: Assertion[Optional[SourceLocationPath]] = asrt.anything_goes(),
        document_parser_exception: Assertion[ParseError] = asrt.anything_goes(),
) -> Assertion[SuiteParseError]:
    return asrt.is_instance_with__many(
        SuiteParseError,
        [
            asrt.sub_component('suite_file',
                               SuiteParseError.suite_file.fget,
                               suite_file
                               ),
            asrt.sub_component('maybe_section_name',
                               SuiteParseError.maybe_section_name.fget,
                               maybe_section_name
                               ),
            asrt.sub_component('source',
                               SuiteParseError.source.fget,
                               source
                               ),
            asrt.sub_component('source_location',
                               SuiteParseError.source_location.fget,
                               source_location
                               ),
            asrt.sub_component('document_parser_exception',
                               SuiteParseError.document_parser_exception.fget,
                               document_parser_exception
                               ),
        ])
