import unittest
from typing import List, Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import file_ref_resolvers2
from exactly_lib.symbol.data import list_resolvers, string_resolvers
from exactly_lib.symbol.data.list_resolver import Element
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType, RelOptionType, RelNonHomeOptionType
from exactly_lib.test_case_utils.parse.parse_relativity import reference_restrictions_for_path_symbol
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_arguments as sut
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    is_any_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import symbol_reference
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_case.test_resources import validation_check
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_utils.parse import parse_list as test_of_list
from exactly_lib_test.test_case_utils.parse.test_resources.invalid_source_tokens import TOKENS_WITH_INVALID_SYNTAX
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opts
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_resources.file_structure import empty_file, DirContents
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestNoElements),
        unittest.makeSuite(TestSingleElement),
        unittest.makeSuite(TestMultipleElements),
    ])


class Expectation:
    def __init__(self,
                 elements: List[Element],
                 validators: asrt.ValueAssertion[Sequence[PreOrPostSdsValidator]],
                 references: asrt.ValueAssertion[Sequence[SymbolReference]],
                 source: asrt.ValueAssertion[ParseSource]):
        self.elements = elements
        self.validators = validators
        self.references = references
        self.source = source


class Case:
    def __init__(self,
                 name: str,
                 source: str,
                 expectation: Expectation):
        self.name = name
        self.source = source
        self.expectation = expectation


class FileRefCase:
    def __init__(self,
                 name: str,
                 relativity_variant: RelativityOptionConfiguration,
                 expected_list_element: Element):
        self.name = name
        self.relativity_variant = relativity_variant
        self.expected_list_element = expected_list_element


class TestInvalidSyntax(unittest.TestCase):
    def test_exception_SHOULD_be_raised_WHEN_invalid_syntax_of_first_element(self):
        for case in TOKENS_WITH_INVALID_SYNTAX:
            with self.subTest(name=case.name,
                              source=case.value):
                source = remaining_source(case.value)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse(source)

    def test_exception_SHOULD_be_raised_WHEN_invalid_syntax_of_second_element(self):
        for case in TOKENS_WITH_INVALID_SYNTAX:
            source = remaining_source('valid' + ' ' + case.value)
            with self.subTest(name=case.name,
                              source=case.value):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse(source)


class TestNoElements(unittest.TestCase):
    def test(self):
        # ARRANGE #
        source_cases = [
            NameAndValue('empty string',
                         ''
                         ),
            NameAndValue('string with only space',
                         '  \t '
                         ),
        ]
        cases = [
            Case(ne.name,
                 ne.value,
                 Expectation(
                     elements=[],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
                     source=asrt_source.is_at_end_of_line(1)
                 ))
            for ne in source_cases
        ]
        # ACT & ASSERT #
        _test_cases(self, cases)


class TestSingleElement(unittest.TestCase):
    def test_string_token(self):
        # ARRANGE #
        plain_string = 'plain'
        symbol_name = 'symbol_name'

        cases = [
            Case('plain string',
                 plain_string,
                 Expectation(
                     elements=[list_resolvers.str_element(plain_string)],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
                     source=asrt_source.is_at_end_of_line(1)
                 )),
            Case('symbol reference',
                 symbol_reference_syntax_for_name(symbol_name),
                 Expectation(
                     elements=[list_resolvers.symbol_element(symbol_reference(symbol_name))],
                     validators=asrt.is_empty_sequence,
                     references=asrt.matches_sequence([asrt_sym_ref.matches_reference_2(
                         symbol_name,
                         is_any_data_type_reference_restrictions())
                     ]),
                     source=asrt_source.is_at_end_of_line(1)
                 )),
        ]
        # ACT & ASSERT #
        _test_cases(self, cases)

    def test_remaining_part_of_current_line_as_literal(self):
        # ARRANGE #
        symbol_name = 'symbol_name'
        str_with_space_and_invalid_token_syntax = 'before and after space, ' + SOFT_QUOTE_CHAR + 'after quote'

        cases = [
            Case('string with one space after marker, and no space at EOL',
                 ' '.join([
                     syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
                     str_with_space_and_invalid_token_syntax]),
                 Expectation(
                     elements=[list_resolvers.str_element(str_with_space_and_invalid_token_syntax)],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
                     source=asrt_source.is_at_end_of_line(1)
                 )),
            Case('with surrounding space',
                 ' '.join([
                     syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
                     '   ' + str_with_space_and_invalid_token_syntax + '  \t ']),
                 Expectation(
                     elements=[list_resolvers.str_element(str_with_space_and_invalid_token_syntax)],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
                     source=asrt_source.is_at_end_of_line(1)
                 )),
            Case('with symbol reference',
                 ' '.join([
                     syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
                     ''.join(['before',
                              symbol_reference_syntax_for_name(symbol_name),
                              'after'])]),
                 Expectation(
                     elements=[list_resolvers.string_element(string_resolvers.from_fragments([
                         string_resolvers.str_fragment('before'),
                         string_resolvers.symbol_fragment(symbol_reference(symbol_name)),
                         string_resolvers.str_fragment('after'),
                     ]))
                     ],
                     validators=asrt.is_empty_sequence,
                     references=asrt.matches_sequence([asrt_sym_ref.matches_reference_2(
                         symbol_name,
                         is_any_data_type_reference_restrictions())
                     ]),
                     source=asrt_source.is_at_end_of_line(1)
                 )),
        ]
        # ACT & ASSERT #
        _test_cases(self, cases)

    def test_existing_file(self):
        # ARRANGE #
        plain_file_name = 'file-name.txt'
        symbol_name = 'symbol_name'

        relativity_cases = [
            FileRefCase('default relativity SHOULD be CASE_HOME',
                        rel_opts.default_conf_rel_home(RelHomeOptionType.REL_HOME_CASE),
                        list_element_for_file_ref(RelOptionType.REL_HOME_CASE, plain_file_name),
                        ),
            FileRefCase('relativity in SDS should be validated post SDS',
                        rel_opts.conf_rel_non_home(RelNonHomeOptionType.REL_TMP),
                        list_element_for_file_ref(RelOptionType.REL_TMP, plain_file_name),
                        ),
            FileRefCase('rel symbol',
                        rel_opts.symbol_conf_rel_home(RelHomeOptionType.REL_HOME_ACT,
                                                      symbol_name,
                                                      sut.REL_OPTIONS_CONF.accepted_relativity_variants),
                        list_resolvers.string_element(
                            string_resolvers.from_file_ref_resolver(
                                file_ref_resolvers2.rel_symbol_with_const_file_name(
                                    SymbolReference(symbol_name,
                                                    reference_restrictions_for_path_symbol(
                                                        sut.REL_OPTIONS_CONF.accepted_relativity_variants
                                                    )),
                                    plain_file_name))),
                        ),
        ]
        for case in relativity_cases:
            with self.subTest(case.name):
                rel_opt_conf = case.relativity_variant
                assert isinstance(rel_opt_conf, RelativityOptionConfiguration)  # Type info for IDE

                _case = Case(
                    'default relativity SHOULD be CASE_HOME',
                    ab.sequence([ab.option(
                        syntax_elements.EXISTING_FILE_OPTION_NAME),
                        rel_opt_conf.file_argument_with_option(
                            plain_file_name)]
                    ).as_str,
                    Expectation(
                        elements=[case.expected_list_element],
                        references=asrt.matches_sequence(rel_opt_conf.symbols.usage_expectation_assertions()),
                        source=asrt_source.is_at_end_of_line(1),
                        validators=is_single_validator_with([
                            NameAndValue('fail when file is missing',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=home_and_sds_populators.empty(),
                                                 symbols=rel_opt_conf.symbols.in_arrangement()),
                                             expectation=
                                             validation_check.fails_on(rel_opt_conf.directory_structure_part),

                                         )),
                            NameAndValue('succeed when file exists',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=
                                                 rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents(
                                                         [empty_file(plain_file_name)])
                                                 ),
                                                 symbols=rel_opt_conf.symbols.in_arrangement()),
                                             expectation=
                                             validation_check.is_success())
                                         ),
                        ]
                        ),
                    )
                )
                _test_case(self, _case)


def is_single_validator_with(expectations: Sequence[NameAndValue[asrt.ValueAssertion[PreOrPostSdsValidator]]]
                             ) -> asrt.ValueAssertion[Sequence[PreOrPostSdsValidator]]:
    return asrt.and_([
        asrt.len_equals(1),
        asrt.on_transformed(pre_or_post_validation.all_of,
                            asrt.all_named(expectations))
    ])


def list_element_for_file_ref(relativity: RelOptionType,
                              name: str) -> Element:
    return list_resolvers.string_element(
        string_resolvers.from_file_ref_resolver(
            file_ref_resolvers2.of_rel_option_with_const_file_name(relativity, name)))


class TestMultipleElements(unittest.TestCase):
    def test(self):
        # ARRANGE #
        plain_string1 = 'plain_1'
        plain_string2 = 'plain_2'
        symbol_name_1 = 'symbol_name_1'
        symbol_name_2 = 'symbol_name_2'
        remaining_part_of_current_line_with_sym_ref = ''.join(['before',
                                                               symbol_reference_syntax_for_name(symbol_name_2),
                                                               'after'])

        cases = [
            Case('plain strings',
                 ab.sequence([plain_string1,
                              plain_string2]).as_str,
                 Expectation(
                     elements=[list_resolvers.str_element(plain_string1),
                               list_resolvers.str_element(plain_string2)],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
                     source=asrt_source.is_at_end_of_line(1)
                 )),
            Case('symbol reference + plain string + until-end-of-line',
                 ab.sequence([ab.symbol_reference(symbol_name_1),
                              plain_string1,
                              syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
                              remaining_part_of_current_line_with_sym_ref,
                              ]).as_str,
                 Expectation(
                     elements=[list_resolvers.symbol_element(symbol_reference(symbol_name_1)),
                               list_resolvers.str_element(plain_string1),
                               list_resolvers.string_element(string_resolvers.from_fragments([
                                   string_resolvers.str_fragment('before'),
                                   string_resolvers.symbol_fragment(symbol_reference(symbol_name_2)),
                                   string_resolvers.str_fragment('after'),
                               ]))
                               ],
                     validators=asrt.is_empty_sequence,
                     references=asrt.matches_sequence([
                         asrt_sym_ref.matches_reference_2(symbol_name_1,
                                                          is_any_data_type_reference_restrictions()),
                         asrt_sym_ref.matches_reference_2(symbol_name_2,
                                                          is_any_data_type_reference_restrictions()),
                     ]),
                     source=asrt_source.is_at_end_of_line(1)
                 )),
        ]
        # ACT & ASSERT #
        _test_cases(self, cases)


def _test_cases(put: unittest.TestCase, cases: Sequence[Case]):
    for case in cases:
        with put.subTest(case.name):
            _test_case(put, case)


def _test_case(put: unittest.TestCase, case: Case) -> ArgumentsResolver:
    # ACT #
    source = remaining_source(case.source)

    actual = sut.parser(consume_last_line_if_is_at_eol_after_parse=False).parse(source)

    # ASSERT #
    expectation = case.expectation
    test_of_list.check_elements(put,
                                expectation.elements,
                                actual.arguments_list)

    expectation.references.apply_with_message(put, actual.references,
                                              'symbol references')

    expectation.validators.apply_with_message(put, actual.validators,
                                              'validators')

    expectation.source.apply_with_message(put, source,
                                          'source')

    return actual
