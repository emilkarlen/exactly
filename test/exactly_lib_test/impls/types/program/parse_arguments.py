import unittest
from typing import List, Sequence

from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.impls.types.path.parse_relativity import reference_restrictions_for_path_symbol
from exactly_lib.impls.types.program.parse import parse_arguments as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs.path_relativity import RelHdsOptionType, RelOptionType, RelNonHdsOptionType
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.list_.list_sdv import ElementSdv
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.impls.types.list_ import parse_list as test_of_list
from exactly_lib_test.impls.types.parse.test_resources.invalid_source_tokens import TOKENS_WITH_INVALID_SYNTAX
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_for_consume_until_end_of_last_line_3
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opts
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import tcds_populators
from exactly_lib_test.test_case.test_resources import validation_check
from exactly_lib_test.test_resources.files.file_structure import DirContents, sym_link, File, Dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_data_rest
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.references import reference_to__on_direct_and_indirect
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import \
    ArgumentOfSymbolReferenceAbsStx, ArgumentOfExistingPathAbsStx, \
    NonSymLinkFileType, ArgumentsAbsStx, ContinuationTokenFollowedByArgumentAbsStx, ArgumentOfRichStringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext


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
                 validators: Assertion[Sequence[DdvValidator]],
                 references: Assertion[Sequence[SymbolReference]]):
        self.elements = elements
        self.validators = validators
        self.references = references


class Case:
    def __init__(self,
                 name: str,
                 source: str,
                 arrangement: Arrangement,
                 expectation: Expectation,
                 ):
        self.name = name
        self.source = source
        self.arrangement = arrangement
        self.expectation = expectation

    @staticmethod
    def of(name: str,
           source: ArgumentAbsStx,
           arrangement: Arrangement,
           expectation: Expectation,
           ) -> 'Case':
        return Case(
            name,
            source.as_str__default(),
            arrangement,
            expectation,
        )

    @staticmethod
    def of_multi(name: str,
                 source: Sequence[ArgumentAbsStx],
                 arrangement: Arrangement,
                 expectation: Expectation,
                 ) -> 'Case':
        return Case(
            name,
            ArgumentsAbsStx(source).as_str__default(),
            arrangement,
            expectation,
        )


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
                    sut.parser().parse(source)

    def test_exception_SHOULD_be_raised_WHEN_invalid_syntax_of_second_element(self):
        for case in TOKENS_WITH_INVALID_SYNTAX:
            source = remaining_source('valid' + ' ' + case.value)
            with self.subTest(name=case.name,
                              source=case.value):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parser().parse(source)

    def test_exception_SHOULD_be_raised_WHEN_first_element_is_reserved_word(self):
        for reserved_word in set(reserved_words.RESERVED_TOKENS).difference(reserved_words.PAREN_END):
            with self.subTest(reserved_word):
                source = remaining_source(reserved_word)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parser().parse(source)

    def test_exception_SHOULD_be_raised_WHEN_second_element_is_reserved_word(self):
        for reserved_word in set(reserved_words.RESERVED_TOKENS).difference(reserved_words.PAREN_END):
            source = remaining_source('valid' + ' ' + reserved_word)
            with self.subTest(reserved_word):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parser().parse(source)


class TestNoElements(unittest.TestCase):
    def test_no_strings(self):
        # ARRANGE #
        source_cases = [
            NameAndValue('empty string',
                         ''
                         ),
            NameAndValue('string with only space',
                         '  \t '
                         ),
            NameAndValue('continuation token followed by empty line',
                         '  {ct}\n '.format(ct=ContinuationTokenFollowedByArgumentAbsStx.CONTINUATION_TOKEN)
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
        _test_cases_w_source_variants(self, cases)

    def test_paren_end(self):
        _test_case(
            self,
            ARRANGEMENT__NEUTRAL,
            Expectation(
                elements=[],
                validators=asrt.is_empty_sequence,
                references=asrt.is_empty_sequence,
            ),
            remaining_source(reserved_words.PAREN_END),
            asrt_source.source_is_not_at_end(
                current_line_number=asrt.equals(1),
                remaining_source=asrt.equals(reserved_words.PAREN_END)
            )
        )


class TestSingleElement(unittest.TestCase):
    def test_string_token(self):
        # ARRANGE #
        plain_string = 'plain'
        symbol_name = 'symbol_name'

        string_symbol = StringSymbolContext.of_arbitrary_value(symbol_name)
        cases = [
            Case.of('plain string',
                    ArgumentOfRichStringAbsStx.of_str(plain_string),
                    ARRANGEMENT__NEUTRAL,
                    Expectation(
                        elements=[list_sdvs.str_element(plain_string)],
                        validators=asrt.is_empty_sequence,
                        references=asrt.is_empty_sequence,
                    )
                    ),
            Case.of('continuation token followed by plain string on next line',
                    ContinuationTokenFollowedByArgumentAbsStx(
                        ArgumentOfRichStringAbsStx.of_str(plain_string)
                    ),
                    ARRANGEMENT__NEUTRAL,
                    Expectation(
                        elements=[list_sdvs.str_element(plain_string)],
                        validators=asrt.is_empty_sequence,
                        references=asrt.is_empty_sequence,
                    )
                    ),
            Case.of('symbol reference',
                    ArgumentOfSymbolReferenceAbsStx(symbol_name),
                    Arrangement(
                        string_symbol.symbol_table
                    ),
                    Expectation(
                        elements=[list_sdvs.symbol_element(reference_to__on_direct_and_indirect(symbol_name))],
                        validators=asrt.is_empty_sequence,
                        references=asrt.matches_sequence([string_symbol.reference_assertion__w_str_rendering]),
                    )
                    ),
        ]
        # ACT & ASSERT #
        _test_cases_w_source_variants(self, cases)

    def test_string_token_followed_by_paren_end(self):
        plain_string = 'plain'
        source = ' '.join((plain_string, reserved_words.PAREN_END))
        _test_case(
            self,
            ARRANGEMENT__NEUTRAL,
            Expectation(
                elements=[list_sdvs.str_element(plain_string)],
                validators=asrt.is_empty_sequence,
                references=asrt.is_empty_sequence,
            ),
            remaining_source(source),
            asrt_source.source_is_not_at_end(
                current_line_number=asrt.equals(1),
                remaining_source=asrt.equals(reserved_words.PAREN_END)
            )
        )

    def test_remaining_part_of_current_line_as_literal(self):
        # ARRANGE #
        symbol_name = 'symbol_name'
        str_with_space_and_invalid_token_syntax = 'before and after space, ' + SOFT_QUOTE_CHAR + 'after quote'

        cases = [
            Case.of('string with one space after marker, and no space at EOL',
                    ArgumentOfRichStringAbsStx.of_str_until_eol(str_with_space_and_invalid_token_syntax),
                    ARRANGEMENT__NEUTRAL,
                    Expectation(
                        elements=[list_sdvs.str_element(str_with_space_and_invalid_token_syntax)],
                        validators=asrt.is_empty_sequence,
                        references=asrt.is_empty_sequence,
                    )),
            Case.of('with surrounding space',
                    ArgumentOfRichStringAbsStx.of_str_until_eol(
                        '   ' + str_with_space_and_invalid_token_syntax + '  \t '
                    ),
                    ARRANGEMENT__NEUTRAL,
                    Expectation(
                        elements=[list_sdvs.str_element(str_with_space_and_invalid_token_syntax)],
                        validators=asrt.is_empty_sequence,
                        references=asrt.is_empty_sequence,
                    )),
            Case.of('with symbol reference',
                    ArgumentOfRichStringAbsStx.of_str_until_eol(
                        ''.join(['before',
                                 symbol_reference_syntax_for_name(symbol_name),
                                 'after'])
                    ),
                    Arrangement(
                        StringSymbolContext.of_arbitrary_value(symbol_name).symbol_table),
                    Expectation(
                        elements=[list_sdvs.string_element(string_sdvs.from_fragments([
                            string_sdvs.str_fragment('before'),
                            string_sdvs.symbol_fragment(reference_to__on_direct_and_indirect(symbol_name)),
                            string_sdvs.str_fragment('after'),
                        ]))
                        ],
                        validators=asrt.is_empty_sequence,
                        references=asrt.matches_sequence([asrt_sym_ref.matches_reference_2(
                            symbol_name,
                            asrt_data_rest.is__w_str_rendering())
                        ]),
                    )),
        ]
        # ACT & ASSERT #
        _test_cases_w_source_variants(self, cases)

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

                _case = Case.of(
                    'default relativity SHOULD be CASE_HOME',
                    ArgumentOfExistingPathAbsStx(
                        rel_opt_conf.path_abs_stx_of_name(plain_file_name),
                        NonSymLinkFileType.REGULAR,
                    ),
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
                _test_case_w_source_variants(self, _case)

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

                _case = Case.of(
                    'default relativity SHOULD be CASE_HOME',
                    ArgumentOfExistingPathAbsStx(
                        rel_opt_conf.path_abs_stx_of_name(checked_file_name),
                        NonSymLinkFileType.DIRECTORY,
                    ),
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
                _test_case_w_source_variants(self, _case)

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

                _case = Case.of(
                    'default relativity SHOULD be CASE_HOME',
                    ArgumentOfExistingPathAbsStx(
                        rel_opt_conf.path_abs_stx_of_name(plain_file_name),
                        None,
                    ),
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
                _test_case_w_source_variants(self, _case)


def is_single_validator_with(expectations: Sequence[NameAndValue[Assertion[DdvValidator]]]
                             ) -> Assertion[Sequence[DdvValidator]]:
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
            Case.of_multi(
                'plain strings',
                [ArgumentOfRichStringAbsStx.of_str(plain_string1),
                 ArgumentOfRichStringAbsStx.of_str(plain_string2)],
                ARRANGEMENT__NEUTRAL,
                Expectation(
                    elements=[list_sdvs.str_element(plain_string1),
                              list_sdvs.str_element(plain_string2)],
                    validators=asrt.is_empty_sequence,
                    references=asrt.is_empty_sequence,
                )),
            Case.of_multi(
                'plain strings on several lines (separated by continuation token)',
                [ArgumentOfRichStringAbsStx.of_str(plain_string1),
                 ContinuationTokenFollowedByArgumentAbsStx(
                     ArgumentOfRichStringAbsStx.of_str(plain_string2)
                 ),
                 ],
                ARRANGEMENT__NEUTRAL,
                Expectation(
                    elements=[list_sdvs.str_element(plain_string1),
                              list_sdvs.str_element(plain_string2)],
                    validators=asrt.is_empty_sequence,
                    references=asrt.is_empty_sequence,
                )),
            Case.of_multi(
                'plain strings on several lines (separated by continuation token) / first line empty',
                [ContinuationTokenFollowedByArgumentAbsStx(
                    ArgumentOfRichStringAbsStx.of_str(plain_string1)
                ),
                    ArgumentOfRichStringAbsStx.of_str(plain_string2),
                ],
                ARRANGEMENT__NEUTRAL,
                Expectation(
                    elements=[list_sdvs.str_element(plain_string1),
                              list_sdvs.str_element(plain_string2)],
                    validators=asrt.is_empty_sequence,
                    references=asrt.is_empty_sequence,
                )),
            Case.of_multi(
                'symbol reference + plain string + until-end-of-line',
                [ArgumentOfSymbolReferenceAbsStx(symbol_name_1),
                 ArgumentOfRichStringAbsStx.of_str(plain_string1),
                 ArgumentOfRichStringAbsStx.of_str_until_eol(remaining_part_of_current_line_with_sym_ref),
                 ],
                Arrangement(
                    SymbolContext.symbol_table_of_contexts([
                        StringSymbolContext.of_arbitrary_value(symbol_name_1),
                        StringSymbolContext.of_arbitrary_value(symbol_name_2),
                    ])
                ),
                Expectation(
                    elements=[list_sdvs.symbol_element(reference_to__on_direct_and_indirect(symbol_name_1)),
                              list_sdvs.str_element(plain_string1),
                              list_sdvs.string_element(string_sdvs.from_fragments([
                                  string_sdvs.str_fragment('before'),
                                  string_sdvs.symbol_fragment(reference_to__on_direct_and_indirect(symbol_name_2)),
                                  string_sdvs.str_fragment('after'),
                              ]))
                              ],
                    validators=asrt.is_empty_sequence,
                    references=asrt.matches_sequence([
                        asrt_sym_ref.matches_reference_2(symbol_name_1,
                                                         asrt_data_rest.is__w_str_rendering()),
                        asrt_sym_ref.matches_reference_2(symbol_name_2,
                                                         asrt_data_rest.is__w_str_rendering()),
                    ]),
                )),
        ]
        # ACT & ASSERT #
        _test_cases_w_source_variants(self, cases)


def _test_cases_w_source_variants(put: unittest.TestCase, cases: Sequence[Case]):
    for case in cases:
        with put.subTest(case.name):
            _test_case_w_source_variants(put, case)


def _test_case_w_source_variants(put: unittest.TestCase, case: Case):
    for source_case in equivalent_source_variants_for_consume_until_end_of_last_line_3(case.source):
        with put.subTest(source_case.name):
            _test_case(put,
                       case.arrangement,
                       case.expectation,
                       source_case.input_value,
                       source_case.expected_value)


def _test_case(put: unittest.TestCase,
               arrangement: Arrangement,
               expectation: Expectation,
               source: ParseSource,
               expected_source_after_parse: Assertion[ParseSource],
               ):
    parser = sut.parser()
    # ACT #

    actual = parser.parse(source)

    # ASSERT #

    expected_source_after_parse.apply_with_message(put, source, 'source after parse')

    test_of_list.check_elements(put,
                                expectation.elements,
                                actual.arguments_list)

    expectation.references.apply_with_message(put, actual.references,
                                              'symbol references')

    actual_ddv = actual.resolve(arrangement.symbols)
    expectation.validators.apply_with_message(put,
                                              actual_ddv.validators,
                                              'validators')
