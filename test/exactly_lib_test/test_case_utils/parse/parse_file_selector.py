import shlex
import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse import parse_file_selector as sut
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_case_utils.parse.test_resources.selection_arguments import name_selector_of, type_selector_of
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestGenericParseProperties),
        unittest.makeSuite(TestFullSelection),
        unittest.makeSuite(TestNamePattern),
        unittest.makeSuite(TestFileType),
        unittest.makeSuite(TestAnd),
    ])


NON_SELECTOR_ARGUMENTS = 'not_a_selector argument'


class ExpectedSelectors:
    def __init__(self,
                 name_patterns: list,
                 file_types: list):
        self.file_types = file_types
        self.name_patterns = name_patterns


def selector_equals(expected: ExpectedSelectors) -> asrt.ValueAssertion:
    return asrt.is_instance_with(Selectors,
                                 asrt.and_([
                                     asrt.sub_component('name_patterns',
                                                        Selectors.name_patterns.fget,
                                                        asrt.equals(frozenset(expected.name_patterns))),
                                     asrt.sub_component('file_types',
                                                        Selectors.file_types.fget,
                                                        asrt.equals(frozenset(expected.file_types))),
                                 ]))


class SourceCase:
    def __init__(self,
                 name: str,
                 source: ParseSource,
                 source_assertion: asrt.ValueAssertion):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion


SPACE = '   '

CASES_WITH_NO_SELECTOR = [

    SourceCase('empty source',
               remaining_source(''),
               assert_source(is_at_eof=asrt.is_true),
               ),
    SourceCase('single line of only space',
               remaining_source(SPACE),
               assert_source(current_line_number=asrt.equals(1),
                             remaining_part_of_current_line=asrt.equals(SPACE)),
               ),
    SourceCase('first line is empty, following lines are non-empty',
               remaining_source(SPACE,
                                ['non-empty following line']),
               assert_source(current_line_number=asrt.equals(1),
                             remaining_part_of_current_line=asrt.equals(SPACE)),
               ),
    SourceCase('first line is empty, following line has a selector',
               remaining_source(SPACE,
                                [name_selector_of('pattern')]),
               assert_source(current_line_number=asrt.equals(1),
                             remaining_part_of_current_line=asrt.equals(SPACE)),
               ),
    SourceCase('argument is non-selector',
               remaining_source(NON_SELECTOR_ARGUMENTS,
                                ['non-empty following line']),
               assert_source(current_line_number=asrt.equals(1),
                             remaining_part_of_current_line=asrt.equals(NON_SELECTOR_ARGUMENTS)),
               ),
]

DESCRIPTION_IS_SINGLE_STR = asrt.matches_sequence([asrt.is_instance(str)])


class Expectation:
    def __init__(self,
                 selectors: ExpectedSelectors,
                 source: asrt.ValueAssertion):
        self.selectors = selectors
        self.source = source


class Arrangement:
    def __init__(self, selector_is_mandatory: bool):
        self.selector_is_mandatory = selector_is_mandatory


class TestGenericParseProperties(unittest.TestCase):
    def test_invalid_argument_ex_SHOULD_be_raised_WHEN_selector_is_mandatory_AND_source_is_not_a_selector(self):
        for case in CASES_WITH_NO_SELECTOR:
            with self.subTest(case=case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_from_parse_source(case.source,
                                                selector_is_mandatory=True)


class TestCaseBase(unittest.TestCase):
    def _check_parse(self,
                     source: ParseSource,
                     arrangement: Arrangement,
                     expectation: Expectation):
        parsed_selector = sut.parse_from_parse_source(source,
                                                      selector_is_mandatory=arrangement.selector_is_mandatory)
        assertion_on_selectors = selector_equals(expectation.selectors)
        assertion_on_selectors.apply_with_message(self, parsed_selector, 'parsed selector')

        expectation.source.apply_with_message(self, source, 'source after parse')


class TestFullSelection(TestCaseBase):
    def test_parse_from_empty_source__and__selector_is_not_mandatory(self):
        for case in CASES_WITH_NO_SELECTOR:
            with self.subTest(case=case.name):
                self._check_parse(
                    case.source,
                    Arrangement(
                        selector_is_mandatory=False,
                    ),
                    Expectation(
                        ExpectedSelectors(name_patterns=[],
                                          file_types=[]),
                        source=case.source_assertion
                    ),
                )


class TestNamePattern(TestCaseBase):
    def test_parse(self):
        pattern = 'include*'
        space = '   '
        for selector_is_mandatory in [False, True]:
            cases = [
                SourceCase('single name argument',
                           remaining_source(name_selector_of(pattern)),
                           assert_source(is_at_eof=asrt.is_true),
                           ),
                SourceCase('single name argument followed by space, and following lines',
                           remaining_source(name_selector_of(pattern) + space,
                                            ['following line']),
                           assert_source(current_line_number=asrt.equals(1),
                                         remaining_part_of_current_line=asrt.equals(space[1:])),
                           ),
                SourceCase('single name argument followed by arguments',
                           remaining_source(name_selector_of(pattern) + space + 'following argument',
                                            ['following line']),
                           assert_source(current_line_number=asrt.equals(1),
                                         remaining_part_of_current_line=asrt.equals(space[1:] + 'following argument')),
                           ),
            ]
            for case in cases:
                with self.subTest(case=case.name,
                                  selector_is_mandatory=str(selector_is_mandatory)):
                    self._check_parse(
                        case.source,
                        Arrangement(
                            selector_is_mandatory=selector_is_mandatory,
                        ),
                        Expectation(
                            ExpectedSelectors(name_patterns=[pattern],
                                              file_types=[],
                                              ),
                            source=case.source_assertion,
                        )
                    )


class TestFileType(TestCaseBase):
    def test_parse(self):
        space = '   '

        def source_cases(file_type: file_properties.FileType) -> list:

            return [
                SourceCase('single name argument',
                           remaining_source(type_selector_of(file_type)),
                           assert_source(is_at_eof=asrt.is_true),
                           ),
                SourceCase('single name argument followed by space, and following lines',
                           remaining_source(type_selector_of(file_type) + space,
                                            ['following line']),
                           assert_source(current_line_number=asrt.equals(1),
                                         remaining_part_of_current_line=asrt.equals(space[1:])),
                           ),
                SourceCase('single name argument followed by arguments',
                           remaining_source(type_selector_of(file_type) + space + name_selector_of('no-matching-file'),
                                            ['following line']),
                           assert_source(current_line_number=asrt.equals(1),
                                         remaining_part_of_current_line=asrt.equals(
                                             space[1:] + name_selector_of('no-matching-file'))),
                           ),
            ]

        for selector_is_mandatory in [False, True]:
            for file_type in FileType:
                for source_case in source_cases(file_type):
                    with self.subTest(case=source_case.name,
                                      file_type=str(file_type),
                                      selector_is_mandatory=str(selector_is_mandatory)):
                        self._check_parse(
                            source_case.source,
                            Arrangement(
                                selector_is_mandatory=selector_is_mandatory,
                            ),
                            Expectation(
                                ExpectedSelectors(name_patterns=[],
                                                  file_types=[file_type])
                                ,
                                source=source_case.source_assertion,
                            ),
                        )


class TestAnd(TestCaseBase):
    def test_parse_SHOULD_fail_WHEN_there_is_an_and_operator_that_is_not_followed_by_a_selector(self):
        for selector_is_mandatory in [False, True]:
            cases = [
                (
                    'and operator as last argument on the line',

                    remaining_source('{selector} {and_}  '.format(
                        selector=name_selector_of('pattern'),
                        and_=sut.AND_OPERATOR),
                        ['following line'])
                ),
                (
                    'and operator is followed by non-selector on the same line',

                    remaining_source('{selector} {and_}  not-a-selector'.format(
                        selector=name_selector_of('pattern'),
                        and_=sut.AND_OPERATOR),
                        ['following line'])
                ),
                (
                    'and operator is the last argument on the line, with a selector on the next line',

                    remaining_source('{selector} {and_}  not-a-selector'.format(
                        selector=name_selector_of('pattern'),
                        and_=sut.AND_OPERATOR),
                        [name_selector_of('pattern-of-selector-on-following-line')])
                ),
            ]
            for name, source in cases:
                with self.subTest(case_name=name,
                                  selector_is_mandatory=selector_is_mandatory):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_from_parse_source(source, selector_is_mandatory)

    def test_parse_one_selector_of_each_type(self):
        name_pattern = 'name pattern'
        file_type = file_properties.FileType.SYMLINK

        remaining_part_of_line = '   arguments after selectors'

        instruction_arguments = '{selector_1} {and_} {selector_2}{remaining_part_of_line}'.format(
            and_=sut.AND_OPERATOR,
            selector_1=name_selector_of(shlex.quote(name_pattern)),
            selector_2=type_selector_of(file_type),
            remaining_part_of_line=remaining_part_of_line)

        for selector_is_mandatory in [False, True]:
            self._check_parse(
                remaining_source(instruction_arguments,
                                 ['following line']),
                Arrangement(
                    selector_is_mandatory=selector_is_mandatory
                ),
                Expectation(
                    ExpectedSelectors(name_patterns=[name_pattern],
                                      file_types=[file_type]),
                    source=assert_source(
                        current_line_number=asrt.equals(1),
                        remaining_part_of_current_line=asrt.equals(remaining_part_of_line[1:]))
                )
            )

    def test_parse_multiple_selectors_of_each_type(self):
        name_pattern_1 = 'name pattern 1'
        name_pattern_2 = 'name pattern 2'
        file_type_1 = file_properties.FileType.REGULAR
        file_type_2 = file_properties.FileType.SYMLINK

        remaining_part_of_line = '   '

        instruction_arguments = (
            '{selector_1} {and_} {selector_2} {and_} {selector_3} {and_} {selector_4}{remaining_part_of_line}'.format(
                and_=sut.AND_OPERATOR,
                selector_1=name_selector_of(shlex.quote(name_pattern_1)),
                selector_2=type_selector_of(file_type_1),
                selector_3=name_selector_of(shlex.quote(name_pattern_2)),
                selector_4=type_selector_of(file_type_2),

                remaining_part_of_line=remaining_part_of_line))

        for selector_is_mandatory in [False, True]:
            self._check_parse(
                remaining_source(instruction_arguments,
                                 ['following line']),
                Arrangement(
                    selector_is_mandatory=selector_is_mandatory
                ),
                Expectation(
                    ExpectedSelectors(name_patterns=[name_pattern_1, name_pattern_2],
                                      file_types=[file_type_1, file_type_2]),
                    source=assert_source(
                        current_line_number=asrt.equals(1),
                        remaining_part_of_current_line=asrt.equals(remaining_part_of_line[1:]))
                )
            )
