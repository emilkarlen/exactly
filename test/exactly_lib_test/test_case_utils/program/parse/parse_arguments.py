import unittest
from typing import List, Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data import list_sdvs, string_sdvs
from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.data.list_sdv import ElementSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType, RelOptionType, RelNonHdsOptionType
from exactly_lib.test_case_utils.parse.parse_relativity import reference_restrictions_for_path_symbol
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_arguments as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    is_any_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import symbol_reference
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.string import StringSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.test_resources import validation_check
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators
from exactly_lib_test.test_case_utils.parse import parse_list as test_of_list
from exactly_lib_test.test_case_utils.parse.test_resources import arguments_building as ab_utils
from exactly_lib_test.test_case_utils.parse.test_resources.invalid_source_tokens import TOKENS_WITH_INVALID_SYNTAX
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_for_consume_until_end_of_last_line
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opts
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_resources.files.file_structure import DirContents, sym_link, File, Dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestNoElements),
        unittest.makeSuite(TestSingleElement),
        unittest.makeSuite(TestMultipleElements),
    ])


class Arrangement:
    def __init__(self,
                 symbols: SymbolTable,
                 ):
        self.symbols = symbols


ARRANGEMENT__NEUTRAL = Arrangement(empty_symbol_table())


class Expectation:
    def __init__(self,
                 elements: List[ElementSdv],
                 validators: ValueAssertion[Sequence[DdvValidator]],
                 references: ValueAssertion[Sequence[SymbolReference]]):
        self.elements = elements
        self.validators = validators
        self.references = references


class Case:
    def __init__(self,
                 name: str,
                 source: str,
                 arrangement: Arrangement,
                 expectation: Expectation):
        self.name = name
        self.source = source
        self.arrangement = arrangement
        self.expectation = expectation


class PathCase:
    def __init__(self,
                 name: str,
                 relativity_variant: RelativityOptionConfiguration,
                 expected_list_element: ElementSdv):
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
                 ARRANGEMENT__NEUTRAL,
                 Expectation(
                     elements=[],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
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

        string_symbol = StringSymbolContext.of_arbitrary_value(symbol_name)
        cases = [
            Case('plain string',
                 plain_string,
                 ARRANGEMENT__NEUTRAL,
                 Expectation(
                     elements=[list_sdvs.str_element(plain_string)],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
                 )),
            Case('symbol reference',
                 symbol_reference_syntax_for_name(symbol_name),
                 Arrangement(
                     string_symbol.symbol_table
                 ),
                 Expectation(
                     elements=[list_sdvs.symbol_element(symbol_reference(symbol_name))],
                     validators=asrt.is_empty_sequence,
                     references=asrt.matches_sequence([string_symbol.reference_assertion__any_data_type]),
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
                 ARRANGEMENT__NEUTRAL,
                 Expectation(
                     elements=[list_sdvs.str_element(str_with_space_and_invalid_token_syntax)],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
                 )),
            Case('with surrounding space',
                 ' '.join([
                     syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
                     '   ' + str_with_space_and_invalid_token_syntax + '  \t ']),
                 ARRANGEMENT__NEUTRAL,
                 Expectation(
                     elements=[list_sdvs.str_element(str_with_space_and_invalid_token_syntax)],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
                 )),
            Case('with symbol reference',
                 ' '.join([
                     syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
                     ''.join(['before',
                              symbol_reference_syntax_for_name(symbol_name),
                              'after'])]),
                 Arrangement(
                     StringSymbolContext.of_arbitrary_value(symbol_name).symbol_table),
                 Expectation(
                     elements=[list_sdvs.string_element(string_sdvs.from_fragments([
                         string_sdvs.str_fragment('before'),
                         string_sdvs.symbol_fragment(symbol_reference(symbol_name)),
                         string_sdvs.str_fragment('after'),
                     ]))
                     ],
                     validators=asrt.is_empty_sequence,
                     references=asrt.matches_sequence([asrt_sym_ref.matches_reference_2(
                         symbol_name,
                         is_any_data_type_reference_restrictions())
                     ]),
                 )),
        ]
        # ACT & ASSERT #
        _test_cases(self, cases)

    def test_existing_regular_file(self):
        # ARRANGE #
        plain_file_name = 'file-name.txt'
        symbol_name = 'symbol_name'

        relativity_cases = [
            PathCase('default relativity SHOULD be CASE_HOME',
                     rel_opts.default_conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
                     list_element_for_path(RelOptionType.REL_HDS_CASE, plain_file_name),
                     ),
            PathCase('relativity in SDS should be validated post SDS',
                     rel_opts.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP),
                     list_element_for_path(RelOptionType.REL_TMP, plain_file_name),
                     ),
            PathCase('rel symbol',
                     rel_opts.symbol_conf_rel_hds(RelHdsOptionType.REL_HDS_ACT,
                                                  symbol_name,
                                                  sut.REL_OPTIONS_CONF.accepted_relativity_variants),
                     list_sdvs.string_element(
                         string_sdvs.from_path_sdv(
                             path_sdvs.rel_symbol_with_const_file_name(
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
                    Arrangement(rel_opt_conf.symbols.in_arrangement()),
                    Expectation(
                        elements=[case.expected_list_element],
                        references=asrt.matches_sequence(rel_opt_conf.symbols.reference_expectation_assertions()),
                        validators=is_single_validator_with([
                            NameAndValue('fail when file is missing',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=tcds_populators.empty()),
                                             expectation=
                                             validation_check.fails_on(rel_opt_conf.directory_structure_partition),

                                         )),
                            NameAndValue('fail when file is a broken sym link',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents([
                                                         sym_link(plain_file_name, 'non-existing-target-file'),
                                                     ])
                                                 )
                                             ),
                                             expectation=
                                             validation_check.fails_on(rel_opt_conf.directory_structure_partition),

                                         )),
                            NameAndValue('succeed when file exists (as regular file)',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=
                                                 rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents(
                                                         [File.empty(plain_file_name)])
                                                 )),
                                             expectation=
                                             validation_check.is_success())
                                         ),
                            NameAndValue('succeed when file exists (as symlink to regular file)',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=
                                                 rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents([
                                                         sym_link(plain_file_name, 'target-file'),
                                                         File.empty('target-file'),
                                                     ])
                                                 )),
                                             expectation=
                                             validation_check.is_success())
                                         ),
                        ]
                        ),
                    )
                )
                _test_case(self, _case)

    def test_existing_dir(self):
        # ARRANGE #
        checked_file_name = 'should-be-a-dir'
        symbol_name = 'symbol_name'

        relativity_cases = [
            PathCase('default relativity SHOULD be CASE_HOME',
                     rel_opts.default_conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
                     list_element_for_path(RelOptionType.REL_HDS_CASE, checked_file_name),
                     ),
            PathCase('relativity in SDS should be validated post SDS',
                     rel_opts.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP),
                     list_element_for_path(RelOptionType.REL_TMP, checked_file_name),
                     ),
            PathCase('rel symbol',
                     rel_opts.symbol_conf_rel_hds(RelHdsOptionType.REL_HDS_ACT,
                                                  symbol_name,
                                                  sut.REL_OPTIONS_CONF.accepted_relativity_variants),
                     list_sdvs.string_element(
                         string_sdvs.from_path_sdv(
                             path_sdvs.rel_symbol_with_const_file_name(
                                 SymbolReference(symbol_name,
                                                 reference_restrictions_for_path_symbol(
                                                     sut.REL_OPTIONS_CONF.accepted_relativity_variants
                                                 )),
                                 checked_file_name))),
                     ),
        ]
        for case in relativity_cases:
            with self.subTest(case.name):
                rel_opt_conf = case.relativity_variant
                assert isinstance(rel_opt_conf, RelativityOptionConfiguration)  # Type info for IDE

                _case = Case(
                    'default relativity SHOULD be CASE_HOME',
                    ab.sequence([ab.option(
                        syntax_elements.EXISTING_DIR_OPTION_NAME),
                        rel_opt_conf.file_argument_with_option(
                            checked_file_name)]
                    ).as_str,
                    Arrangement(rel_opt_conf.symbols.in_arrangement()),
                    Expectation(
                        elements=[case.expected_list_element],
                        references=asrt.matches_sequence(rel_opt_conf.symbols.reference_expectation_assertions()),
                        validators=is_single_validator_with([
                            NameAndValue('fail when file is missing',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=tcds_populators.empty()),
                                             expectation=
                                             validation_check.fails_on(rel_opt_conf.directory_structure_partition),

                                         )),
                            NameAndValue('fail when file is is a regular file',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents([
                                                         File.empty(checked_file_name),
                                                     ])
                                                 )
                                             ),
                                             expectation=
                                             validation_check.fails_on(rel_opt_conf.directory_structure_partition),

                                         )),
                            NameAndValue('fail when file is a broken sym link',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents([
                                                         sym_link(checked_file_name, 'non-existing-target-file'),
                                                     ])
                                                 )
                                             ),
                                             expectation=
                                             validation_check.fails_on(rel_opt_conf.directory_structure_partition),

                                         )),
                            NameAndValue('succeed when file exists (as a dir)',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=
                                                 rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents([
                                                         Dir.empty(checked_file_name),
                                                     ])
                                                 )),
                                             expectation=
                                             validation_check.is_success())
                                         ),
                            NameAndValue('succeed when file exists (as symlink to dir)',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=
                                                 rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents([
                                                         sym_link(checked_file_name, 'target-file'),
                                                         Dir.empty('target-file'),
                                                     ])
                                                 )),
                                             expectation=
                                             validation_check.is_success())
                                         ),
                        ]
                        ),
                    )
                )
                _test_case(self, _case)

    def test_existing_path(self):
        # ARRANGE #
        plain_file_name = 'path-name'
        symbol_name = 'symbol_name'

        relativity_cases = [
            PathCase('default relativity SHOULD be CASE_HOME',
                     rel_opts.default_conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
                     list_element_for_path(RelOptionType.REL_HDS_CASE, plain_file_name),
                     ),
            PathCase('relativity in SDS should be validated post SDS',
                     rel_opts.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP),
                     list_element_for_path(RelOptionType.REL_TMP, plain_file_name),
                     ),
            PathCase('rel symbol',
                     rel_opts.symbol_conf_rel_hds(RelHdsOptionType.REL_HDS_ACT,
                                                  symbol_name,
                                                  sut.REL_OPTIONS_CONF.accepted_relativity_variants),
                     list_sdvs.string_element(
                         string_sdvs.from_path_sdv(
                             path_sdvs.rel_symbol_with_const_file_name(
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
                        syntax_elements.EXISTING_PATH_OPTION_NAME),
                        rel_opt_conf.file_argument_with_option(
                            plain_file_name)]
                    ).as_str,
                    Arrangement(rel_opt_conf.symbols.in_arrangement()),
                    Expectation(
                        elements=[case.expected_list_element],
                        references=asrt.matches_sequence(rel_opt_conf.symbols.reference_expectation_assertions()),
                        validators=is_single_validator_with([
                            NameAndValue('fail when file is missing',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=tcds_populators.empty()),
                                             expectation=
                                             validation_check.fails_on(rel_opt_conf.directory_structure_partition),

                                         )),
                            NameAndValue('fail when file is a broken sym link',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents([
                                                         sym_link(plain_file_name, 'non-existing-target-file'),
                                                     ])
                                                 )
                                             ),
                                             expectation=
                                             validation_check.fails_on(rel_opt_conf.directory_structure_partition),

                                         )),
                            NameAndValue('succeed when file exists (as regular file)',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=
                                                 rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents(
                                                         [File.empty(plain_file_name)])
                                                 )),
                                             expectation=
                                             validation_check.is_success())
                                         ),
                            NameAndValue('succeed when file exists (as symlink to regular file)',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=
                                                 rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents([
                                                         sym_link(plain_file_name, 'target-file'),
                                                         File.empty('target-file'),
                                                     ])
                                                 )),
                                             expectation=
                                             validation_check.is_success())
                                         ),
                            NameAndValue('succeed when file exists (as a dir)',
                                         validation_check.assert_with_files(
                                             arrangement=
                                             validation_check.Arrangement(
                                                 dir_contents=
                                                 rel_opt_conf.populator_for_relativity_option_root(
                                                     DirContents([
                                                         Dir.empty(plain_file_name),
                                                     ])
                                                 )),
                                             expectation=
                                             validation_check.is_success())
                                         ),
                        ]
                        ),
                    )
                )
                _test_case(self, _case)


def is_single_validator_with(expectations: Sequence[NameAndValue[ValueAssertion[DdvValidator]]]
                             ) -> ValueAssertion[Sequence[DdvValidator]]:
    return asrt.and_([
        asrt.len_equals(1),
        asrt.on_transformed(ddv_validators.all_of,
                            asrt.all_named(expectations))
    ])


def list_element_for_path(relativity: RelOptionType,
                          name: str) -> ElementSdv:
    return list_sdvs.string_element(
        string_sdvs.from_path_sdv(
            path_sdvs.of_rel_option_with_const_file_name(relativity, name)))


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
                 ARRANGEMENT__NEUTRAL,
                 Expectation(
                     elements=[list_sdvs.str_element(plain_string1),
                               list_sdvs.str_element(plain_string2)],
                     validators=asrt.is_empty_sequence,
                     references=asrt.is_empty_sequence,
                 )),
            Case('symbol reference + plain string + until-end-of-line',
                 ab.sequence([ab.symbol_reference(symbol_name_1),
                              plain_string1,
                              syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
                              remaining_part_of_current_line_with_sym_ref,
                              ]).as_str,
                 Arrangement(
                     SymbolContext.symbol_table_of_contexts([
                         StringSymbolContext.of_arbitrary_value(symbol_name_1),
                         StringSymbolContext.of_arbitrary_value(symbol_name_2),
                     ])
                 ),
                 Expectation(
                     elements=[list_sdvs.symbol_element(symbol_reference(symbol_name_1)),
                               list_sdvs.str_element(plain_string1),
                               list_sdvs.string_element(string_sdvs.from_fragments([
                                   string_sdvs.str_fragment('before'),
                                   string_sdvs.symbol_fragment(symbol_reference(symbol_name_2)),
                                   string_sdvs.str_fragment('after'),
                               ]))
                               ],
                     validators=asrt.is_empty_sequence,
                     references=asrt.matches_sequence([
                         asrt_sym_ref.matches_reference_2(symbol_name_1,
                                                          is_any_data_type_reference_restrictions()),
                         asrt_sym_ref.matches_reference_2(symbol_name_2,
                                                          is_any_data_type_reference_restrictions()),
                     ]),
                 )),
        ]
        # ACT & ASSERT #
        _test_cases(self, cases)


def _test_cases(put: unittest.TestCase, cases: Sequence[Case]):
    for case in cases:
        with put.subTest(case.name):
            _test_case(put, case)


def _test_case(put: unittest.TestCase, case: Case):
    parser = sut.parser()
    # ACT #

    source_as_arguments = ab_utils.Arguments(case.source)
    for parse_source, parse_source_assertion in equivalent_source_variants_for_consume_until_end_of_last_line(
            source_as_arguments):
        actual = parser.parse(parse_source)

        # ASSERT #

        parse_source_assertion.apply_with_message(put, parse_source, 'parse source')

        expectation = case.expectation
        test_of_list.check_elements(put,
                                    expectation.elements,
                                    actual.arguments_list)

        expectation.references.apply_with_message(put, actual.references,
                                                  'symbol references')

        actual_ddv = actual.resolve(case.arrangement.symbols)
        expectation.validators.apply_with_message(put,
                                                  actual_ddv.validators,
                                                  'validators')
