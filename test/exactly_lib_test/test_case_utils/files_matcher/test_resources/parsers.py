from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib.util.name_and_value import NameAndValue

TOP_LEVEL_PARSER_CASES = [
    NameAndValue(
        'top level parser/simple expr',
        sut.parsers().simple,
    ),
    NameAndValue(
        'top level parser/full expr',
        sut.parsers().full,
    ),
]
