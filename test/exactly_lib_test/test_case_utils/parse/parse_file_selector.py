import shlex
import unittest

from exactly_lib.named_element.file_selectors import FileSelectorConstant
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.parse import parse_file_selector as sut
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.type_system_values.value_type import ElementType
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.named_element.file_selector.test_resources.file_selector_resolver_assertions import \
    resolved_value_equals_file_selector
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as asrt_ne
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.named_element.test_resources.restrictions_assertions import is_element_type_restriction
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_case_utils.parse.test_resources.selection_arguments import name_selector_of, type_selector_of
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestGenericParseProperties),
        unittest.makeSuite(TestNamePattern),
        unittest.makeSuite(TestFileType),
        unittest.makeSuite(TestAnd),
        unittest.makeSuite(TestReference),
    ])


NON_SELECTOR_ARGUMENTS = 'not_a_selector argument'


def expected_selector(name_patterns: list = (),
                      file_types: list = (),
                      references: asrt.ValueAssertion = asrt.is_empty_list) -> asrt.ValueAssertion:
    expected = file_selector_of(name_patterns, file_types)
    return resolved_value_equals_file_selector(expected,
                                               expected_references=references)


def file_selector_of(name_patterns: list = (),
                     file_types: list = ()) -> sut.FileSelector:
    return FileSelector(Selectors(name_patterns=frozenset(name_patterns),
                                  file_types=frozenset(file_types)))


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
               remaining_source('invalid-element-name',
                                ['non-empty following line']),
               assert_source(current_line_number=asrt.equals(1),
                             remaining_part_of_current_line=asrt.equals('invalid-element-name')),
               ),
    SourceCase('argument is non-selector',
               remaining_source(str(surrounded_by_hard_quotes('name_must_not_be_quoted')),
                                ['non-empty following line']),
               assert_source(current_line_number=asrt.equals(1),
                             remaining_part_of_current_line=asrt.equals('name_must_not_be_quoted')),
               ),
]

DESCRIPTION_IS_SINGLE_STR = asrt.matches_sequence([asrt.is_instance(str)])


class Expectation:
    def __init__(self,
                 selector: asrt.ValueAssertion,
                 source: asrt.ValueAssertion,
                 ):
        self.selector = selector
        self.source = source


class TestGenericParseProperties(unittest.TestCase):
    def test_invalid_argument_ex_SHOULD_be_raised_WHEN_source_is_not_a_selector(self):
        for case in CASES_WITH_NO_SELECTOR:
            with self.subTest(case=case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_resolver_from_parse_source(case.source)


class TestCaseBase(unittest.TestCase):
    def _check_parse(self,
                     source: ParseSource,
                     expectation: Expectation):
        parsed_selector_resolver = sut.parse_resolver_from_parse_source(source)

        expectation.selector.apply_with_message(self, parsed_selector_resolver,
                                                'parsed selector resolver')

        expectation.source.apply_with_message(self, source, 'source after parse')


class TestNamePattern(TestCaseBase):
    def test_parse(self):
        pattern = 'include*'
        space = '   '
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
            with self.subTest(case=case.name):
                self._check_parse(
                    case.source,
                    Expectation(
                        expected_selector(name_patterns=[pattern],
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

        for file_type in FileType:
            for source_case in source_cases(file_type):
                with self.subTest(case=source_case.name,
                                  file_type=str(file_type)):
                    self._check_parse(
                        source_case.source,
                        Expectation(
                            expected_selector(name_patterns=[],
                                              file_types=[file_type])
                            ,
                            source=source_case.source_assertion,
                        ),
                    )


class TestAnd(TestCaseBase):
    def test_parse_SHOULD_fail_WHEN_there_is_an_and_operator_that_is_not_followed_by_a_selector(self):
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
                'and operator is followed by non-selector (quoted) on the same line',

                remaining_source('{selector} {and_}  {command_name_in_quotes}'.format(
                    selector=name_selector_of('pattern'),
                    and_=sut.AND_OPERATOR,
                    command_name_in_quotes=surrounded_by_hard_quotes(sut.COMMAND_NAME__NAME_SELECTOR)),
                    ['following line'])
            ),
            (
                'and operator is the last argument on the line, with a selector on the next line',

                remaining_source('{selector} {and_}  '.format(
                    selector=name_selector_of('pattern'),
                    and_=sut.AND_OPERATOR),
                    [name_selector_of('pattern-of-selector-on-following-line')])
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_resolver_from_parse_source(source)

    def test_parse_one_selector_of_each_type(self):
        name_pattern = 'name pattern'
        file_type = file_properties.FileType.SYMLINK

        remaining_part_of_line = '   arguments after selectors'

        instruction_arguments = '{selector_1} {and_} {selector_2}{remaining_part_of_line}'.format(
            and_=sut.AND_OPERATOR,
            selector_1=name_selector_of(shlex.quote(name_pattern)),
            selector_2=type_selector_of(file_type),
            remaining_part_of_line=remaining_part_of_line)

        self._check_parse(
            remaining_source(instruction_arguments,
                             ['following line']),
            Expectation(
                expected_selector(name_patterns=[name_pattern],
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

        self._check_parse(
            remaining_source(instruction_arguments,
                             ['following line']),
            Expectation(
                expected_selector(name_patterns=[name_pattern_1, name_pattern_2],
                                  file_types=[file_type_1, file_type_2]),
                source=assert_source(
                    current_line_number=asrt.equals(1),
                    remaining_part_of_current_line=asrt.equals(remaining_part_of_line[1:]))
            )
        )


class TestReference(TestCaseBase):
    def test_WHEN_legal_syntax_and_legal_name_THEN_parse_SHOULD_succeed(self):
        reffed_selector = NameAndValue(
            'name_of_selector',
            file_selector_of(name_patterns=['pattern'])
        )
        expected_references = asrt.matches_sequence([
            asrt_ne.matches_reference(asrt.equals(reffed_selector.name),
                                      is_element_type_restriction(ElementType.LOGIC))
        ])
        named_elements = singleton_symbol_table_2(reffed_selector.name,
                                                  container(FileSelectorConstant(reffed_selector.value)))
        space = '   '
        cases = [
            SourceCase('single name argument followed by space, and following lines',
                       remaining_source(reffed_selector.name + space,
                                        ['following line']),
                       assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(space[1:])),
                       ),
        ]
        for case in cases:
            with self.subTest(case=case.name):
                self._check_parse(
                    case.source,
                    Expectation(
                        selector=resolved_value_equals_file_selector(reffed_selector.value,
                                                                     expected_references,
                                                                     named_elements),
                        source=case.source_assertion,
                    )
                )

    def test_and_operator_with_references(self):
        name_pattern = 'name-pattern'
        file_type = FileType.SYMLINK
        reffed_selector = NameAndValue(
            'name_of_selector',
            file_selector_of(file_types=[file_type])
        )

        expected_resolved_selector = file_selector_of(name_patterns=[name_pattern],
                                                      file_types=[file_type])
        expected_references = asrt.matches_sequence([
            asrt_ne.matches_reference(asrt.equals(reffed_selector.name),
                                      is_element_type_restriction(ElementType.LOGIC))
        ])
        named_elements = singleton_symbol_table_2(reffed_selector.name,
                                                  container(FileSelectorConstant(reffed_selector.value)))
        space = '   '
        instruction_arguments = '{concrete_selector} {and_} {selector_reference}'.format(
            and_=sut.AND_OPERATOR,
            concrete_selector=name_selector_of(shlex.quote(name_pattern)),
            selector_reference=reffed_selector.name,
        )
        source_cases = [
            SourceCase('single name argument followed by space, and following lines',
                       remaining_source(instruction_arguments + space,
                                        ['following line']),
                       assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(space[1:])),
                       ),
            SourceCase('single name argument followed by space, and AND operator on following line',
                       remaining_source(instruction_arguments + space,
                                        [sut.AND_OPERATOR]),
                       assert_source(current_line_number=asrt.equals(1),
                                     remaining_part_of_current_line=asrt.equals(space[1:])),
                       ),
        ]
        for case in source_cases:
            with self.subTest(case=case.name):
                self._check_parse(
                    case.source,
                    Expectation(
                        selector=resolved_value_equals_file_selector(expected_resolved_selector,
                                                                     expected_references,
                                                                     named_elements),
                        source=case.source_assertion,
                    )
                )

    def test_WHEN_name_has_illegal_syntax_THEN_parse_SHOULD_fail(self):
        cases = [
            str(surrounded_by_hard_quotes(sut.COMMAND_NAME__TYPE_SELECTOR)),
            'illegal-name'
        ]
        for argument_string in cases:
            source = remaining_source(argument_string)
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                sut.parse_resolver_from_parse_source(source)
