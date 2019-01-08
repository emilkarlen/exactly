import unittest

import pathlib
import shlex

from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.files_matcher import FilesMatcherResolver
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerConstant
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import expression, integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources import model
from exactly_lib_test.test_case_utils.files_matcher.test_resources import tr
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    FilesContentsAssertionVariant, FilesMatcherArgumentsSetup, \
    files_matcher_setup_without_references
from exactly_lib_test.test_case_utils.files_matcher.test_resources.check_with_neg_and_rel_opts import \
    MatcherChecker
from exactly_lib_test.test_case_utils.files_matcher.test_resources.expression import int_condition
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import \
    arguments_building as string_matcher_args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import \
    EmptyAssertionArgumentsConstructor, NumLinesAssertionArgumentsConstructor, EqualsStringAssertionArgumentsConstructor
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.contents_transformation import \
    ToUppercaseStringTransformer
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions as asrt_matcher
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail, expectation_type_config__non_is_success
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, File, Dir, empty_dir, sym_link
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseInvalidSyntax),

        unittest.makeSuite(TestCommonFailureConditions),

        unittest.makeSuite(TestSymbolReferences),

        unittest.makeSuite(TestFailingValidationPreSdsDueToInvalidIntegerArgumentOfNumLines),

        unittest.makeSuite(TestHardErrorWhenAFileThatIsNotARegularFileIsTested),

        unittest.makeSuite(TestExistsEmptyFile),
        unittest.makeSuite(TestForAllEmptyFile),

        unittest.makeSuite(TestOnlyFilesSelectedByTheFileMatcherShouldBeChecked),

        unittest.makeSuite(TestAssertionVariantThatTransformersMultipleFiles),
    ])


class TestWithAssertionVariantForFileContents(tr.TestWithAssertionVariantBase):
    @property
    def assertion_variant(self) -> FilesMatcherArgumentsSetup:
        return files_matcher_setup_without_references(
            FilesContentsAssertionVariant(
                Quantifier.ALL,
                file_contents_arg(EmptyAssertionArgumentsConstructor()),
            )
        )


def file_contents_arg(
        contents_variant: string_matcher_args.FileContentsArgumentsConstructor,
        common: string_matcher_args.CommonArgumentsConstructor = string_matcher_args.CommonArgumentsConstructor()
) -> string_matcher_args.ImplicitActualFileArgumentsConstructor:
    return string_matcher_args.ImplicitActualFileArgumentsConstructor(
        common,
        contents_variant)


class TestParseInvalidSyntax(tr.TestParseInvalidSyntaxBase,
                             TestWithAssertionVariantForFileContents):
    pass


class TestCommonFailureConditions(tr.TestCommonFailureConditionsBase,
                                  TestWithAssertionVariantForFileContents):
    pass


class TestFailingValidationPreSdsDueToInvalidIntegerArgumentOfNumLines(expression.TestFailingValidationPreSdsAbstract):
    def _conf(self) -> expression.Configuration:
        return expression.Configuration(sut.files_matcher_parser(),
                                        TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(),
                                        invalid_integers_according_to_custom_validation=[-1, -2])


class TheInstructionArgumentsVariantConstructorForIntegerResolvingOfNumFilesCheck(
    expression.InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given comparision condition string.
    """

    def apply(self, condition_str: str) -> str:
        arguments_constructor = args.complete_arguments_constructor(
            FilesContentsAssertionVariant(
                Quantifier.ALL,
                file_contents_arg(NumLinesAssertionArgumentsConstructor(condition_str))))
        return arguments_constructor.apply(expectation_type_config__non_is_success(ExpectationType.POSITIVE))


class TestSymbolReferences(tr.TestCommonSymbolReferencesBase,
                           TestWithAssertionVariantForFileContents):
    def test_symbols_from_contents_assertion_SHOULD_be_reported(self):
        # ARRANGE #

        operand_sym_ref = SymbolReference('operand_symbol_name',
                                          string_made_up_by_just_strings())

        condition_str = '{operator} {symbol_reference}'.format(
            operator=comparators.EQ.name,
            symbol_reference=symbol_reference_syntax_for_name(operand_sym_ref.name)
        )
        arguments_constructor = args.complete_arguments_constructor(
            FilesContentsAssertionVariant(
                Quantifier.ALL,
                file_contents_arg(NumLinesAssertionArgumentsConstructor(condition_str))))

        argument = arguments_constructor.apply(expectation_type_config__non_is_success(ExpectationType.NEGATIVE))

        source = remaining_source(argument)

        # ACT #

        matcher_resolver = sut.files_matcher_parser().parse(source)

        assert isinstance(matcher_resolver, FilesMatcherResolver)

        actual_symbol_references = matcher_resolver.references

        # ASSERT #

        expected_symbol_references = [
            operand_sym_ref,
        ]
        assertion = equals_symbol_references(expected_symbol_references)

        assertion.apply_without_message(self, actual_symbol_references)


class TestHardErrorWhenAFileThatIsNotARegularFileIsTested(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    file_content_assertion_variants = [
        EmptyAssertionArgumentsConstructor(),
        NumLinesAssertionArgumentsConstructor(int_condition(comparators.NE, 0)),
        EqualsStringAssertionArgumentsConstructor('expected'),
    ]

    def test_hard_error_when_there_is_a_single_file_that_is_not_a_regular_file(self):
        parser = sut.files_matcher_parser()

        name_of_checked_dir = 'checked-dir'
        relativity_root_conf = rel_opt_conf.default_conf_rel_any(RelOptionType.REL_CWD)
        the_model = model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir)(relativity_root_conf)

        non_regular_files = [
            empty_dir('a-directory'),
            sym_link('sym-link', 'non-existing-target')
        ]

        for file_contents_assertion in self.file_content_assertion_variants:
            for quantifier in Quantifier:
                arguments_constructor = args.complete_arguments_constructor(
                    FilesContentsAssertionVariant(
                        quantifier,
                        file_contents_arg(file_contents_assertion)))
                for expectation_type in ExpectationType:
                    arguments = arguments_constructor.apply(
                        expectation_type_config__non_is_success(expectation_type))
                    for non_regular_file in non_regular_files:
                        with self.subTest(
                                quantifier=quantifier.name,
                                expectation_type=expectation_type.name,
                                arguments=arguments,
                                non_regular_file=non_regular_file.name):
                            integration_check.check(
                                self,
                                parser,
                                remaining_source(arguments),
                                the_model,
                                arrangement=
                                ArrangementPostAct(
                                    home_or_sds_contents=relativity_root_conf.populator_for_relativity_option_root(
                                        DirContents([
                                            Dir(name_of_checked_dir, [
                                                non_regular_file,
                                            ]),
                                        ])
                                    )
                                ),
                                expectation=
                                Expectation(
                                    is_hard_error=asrt_matcher.is_hard_error()
                                )
                            )


AN_ACCEPTED_SDS_REL_OPT_CONFIG = rel_opt_conf.conf_rel_sds(RelSdsOptionType.REL_TMP)


class TestExistsEmptyFile(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    exists__empty__arguments = args.complete_arguments_constructor(
        FilesContentsAssertionVariant(
            Quantifier.EXISTS,
            file_contents_arg(EmptyAssertionArgumentsConstructor()))
    )

    @property
    def instruction_checker(self) -> MatcherChecker:
        return MatcherChecker(self, sut.files_matcher_parser())

    def test_one_empty_and_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            main_result_for_positive_expectation=PassOrFail.PASS,
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    empty_file('empty-file.txt'),
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_just_one_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    empty_file('empty-file.txt'),
                ]),
            ]),
        )

    def test_just_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_no_files(self):
        self.instruction_checker.check_expectation_type_variants(
            self.exists__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, []),
            ]),
        )


class TestForAllEmptyFile(unittest.TestCase):
    name_of_checked_dir = 'checked-dir'
    for_all__empty__arguments = args.complete_arguments_constructor(
        FilesContentsAssertionVariant(
            Quantifier.ALL,
            file_contents_arg(EmptyAssertionArgumentsConstructor()))
    )

    @property
    def instruction_checker(self) -> MatcherChecker:
        return MatcherChecker(self, sut.files_matcher_parser())

    def test_one_empty_and_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            main_result_for_positive_expectation=PassOrFail.FAIL,
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    empty_file('empty-file.txt'),
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_just_one_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    empty_file('empty-file.txt'),
                ]),
            ]),
        )

    def test_just_one_non_empty_file(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.FAIL,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, [
                    File('non-empty-file.txt', 'contents of non-empty file'),
                ]),
            ]),
        )

    def test_no_files(self):
        self.instruction_checker.check_expectation_type_variants(
            self.for_all__empty__arguments,
            model.model_with_source_path_as_sub_dir_of_rel_root(self.name_of_checked_dir),
            root_dir_of_dir_contents=AN_ACCEPTED_SDS_REL_OPT_CONFIG,
            main_result_for_positive_expectation=PassOrFail.PASS,
            contents_of_relativity_option_root=DirContents([
                Dir(self.name_of_checked_dir, []),
            ]),
        )


class TestOnlyFilesSelectedByTheFileMatcherShouldBeChecked(unittest.TestCase):
    file_content_assertion_variants_that_pass_iff_file_is_empty = [
        EmptyAssertionArgumentsConstructor(),
        NumLinesAssertionArgumentsConstructor(int_condition(comparators.EQ, 0)),
        EqualsStringAssertionArgumentsConstructor(shlex.quote('')),
    ]

    def test__all__SHOULD_consider_only_files_matched_by_the_file_matcher(self):
        # ARRANGE #
        parser = sut.files_matcher_parser()
        name_of_checked_dir = 'name-of-checked-dir'

        name_starts_with_selected = NameAndValue(
            'a_file_matcher_symbol',
            FileMatcherThatMatchesAnyFileWhosNameStartsWith('selected'))

        files_in_checked_dir = Dir(name_of_checked_dir, [
            empty_file(
                'selected-empty-file.txt'),
            File(
                'un-selected-non-empty-file.txt', 'contents of non-emtpy file'),
            empty_dir(
                'un-selected-dir'),
            sym_link(
                'un-selected-sym-link-to-dir', 'un-selected-dir'),
            sym_link(
                'un-selected-broken-sym-link', 'non-existing-file'),
        ])

        symbol_table_with_file_matcher = SymbolTable({
            name_starts_with_selected.name: container(FileMatcherConstantResolver(name_starts_with_selected.value))
        })
        relativity_root_conf = AN_ACCEPTED_SDS_REL_OPT_CONFIG

        expected_symbol_references = asrt.matches_sequence([
            is_file_matcher_reference_to(name_starts_with_selected.name)
        ])

        # ACT & ASSERT #

        for file_is_empty_assertion in self.file_content_assertion_variants_that_pass_iff_file_is_empty:
            arguments_constructor = args.complete_arguments_constructor(
                FilesContentsAssertionVariant(
                    Quantifier.ALL,
                    file_contents_arg(file_is_empty_assertion)),
                file_matcher=name_starts_with_selected.name
            )
            for expectation_type in ExpectationType:
                etc = expectation_type_config__non_is_success(expectation_type)
                arguments = arguments_constructor.apply(etc)
                with self.subTest(
                        expectation_type=expectation_type.name,
                        arguments=arguments):
                    integration_check.check(
                        self,
                        parser,
                        remaining_source(arguments),
                        model.model_with_source_path_as_sub_dir_of_rel_root(name_of_checked_dir)(relativity_root_conf),
                        arrangement=
                        ArrangementPostAct(
                            home_or_sds_contents=relativity_root_conf.populator_for_relativity_option_root(
                                DirContents([
                                    files_in_checked_dir,
                                ])
                            ),
                            symbols=symbol_table_with_file_matcher
                        ),
                        expectation=
                        Expectation(
                            main_result=etc.pass__if_positive__fail__if_negative,
                            symbol_usages=expected_symbol_references
                        )
                    )

    def test__exists__SHOULD_consider_only_files_matched_by_the_file_matcher(self):
        # ARRANGE #
        parser = sut.files_matcher_parser()
        name_of_checked_dir = 'name-of-checked-dir'

        name_starts_with_selected = NameAndValue(
            'a_file_matcher_symbol',
            FileMatcherThatMatchesAnyFileWhosNameStartsWith('selected'))

        files_in_checked_dir = Dir(name_of_checked_dir, [
            File(
                'selected-non-empty-file.txt', 'contents of non-emtpy file'),
            empty_file(
                'un-selected-empty-file.txt'),
            empty_dir(
                'un-selected-dir'),
            sym_link(
                'un-selected-sym-link-to-dir', 'un-selected-dir'),
            sym_link(
                'un-selected-broken-sym-link', 'non-existing-file'),
        ])

        symbol_table_with_file_matcher = SymbolTable({
            name_starts_with_selected.name: container(FileMatcherConstantResolver(name_starts_with_selected.value))
        })
        relativity_root_conf = AN_ACCEPTED_SDS_REL_OPT_CONFIG

        expected_symbol_references = asrt.matches_sequence([
            is_file_matcher_reference_to(name_starts_with_selected.name)
        ])

        # ACT & ASSERT #

        for file_is_empty_assertion in self.file_content_assertion_variants_that_pass_iff_file_is_empty:
            arguments_constructor = args.complete_arguments_constructor(
                FilesContentsAssertionVariant(
                    Quantifier.EXISTS,
                    file_contents_arg(file_is_empty_assertion)),
                file_matcher=name_starts_with_selected.name
            )
            for expectation_type in ExpectationType:
                etc = expectation_type_config__non_is_success(expectation_type)
                arguments = arguments_constructor.apply(etc)
                with self.subTest(
                        expectation_type=expectation_type.name,
                        arguments=arguments):
                    integration_check.check(
                        self,
                        parser,
                        remaining_source(arguments),
                        model.model_with_source_path_as_sub_dir_of_rel_root(name_of_checked_dir)(relativity_root_conf),
                        arrangement=
                        ArrangementPostAct(
                            home_or_sds_contents=relativity_root_conf.populator_for_relativity_option_root(
                                DirContents([
                                    files_in_checked_dir,
                                ])
                            ),
                            symbols=symbol_table_with_file_matcher
                        ),
                        expectation=
                        Expectation(
                            main_result=etc.fail__if_positive__pass_if_negative,
                            symbol_usages=expected_symbol_references
                        )
                    )


class TestAssertionVariantThatTransformersMultipleFiles(unittest.TestCase):
    """
    The "equals" assertion variant needs to create intermediate files (as of 2017-09-17).
    This means that the integration of the file contents assertion ("equals") must provide
    the ability to create these files.

    The difference between the "file contents" and "dir contents"
    case is that multiple intermediate files may need to be created by "dir contents".
    """
    name_of_checked_dir = 'checked-dir'

    @property
    def instruction_checker(self) -> MatcherChecker:
        return MatcherChecker(self, sut.files_matcher_parser())

    def test_it_SHOULD_be_possible_to_create_multiple_intermediate_files(self):
        # ARRANGE #
        original_file_contents = 'original_file_contents'
        expected_transformer_contents = original_file_contents.upper()

        transform_to_uppercase = NameAndValue(
            'to_uppercase_lines_transformer',
            ToUppercaseStringTransformer())

        symbol_table_with_lines_transformer = SymbolTable({
            transform_to_uppercase.name: container(StringTransformerConstant(transform_to_uppercase.value))
        })
        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_transformer(transform_to_uppercase.name)
        ])

        for_all__equals__arguments = args.complete_arguments_constructor(
            FilesContentsAssertionVariant(
                Quantifier.ALL,
                string_matcher_args.ImplicitActualFileArgumentsConstructor(
                    string_matcher_args.CommonArgumentsConstructor(
                        file_transformer=transform_to_uppercase.name),
                    EqualsStringAssertionArgumentsConstructor(expected_transformer_contents)),
            ))
        relativity_root_conf = AN_ACCEPTED_SDS_REL_OPT_CONFIG
        etc = expectation_type_config__non_is_success(ExpectationType.POSITIVE)
        arguments = for_all__equals__arguments.apply(etc)
        # ACT & ASSERT #
        integration_check.check(
            self,
            sut.files_matcher_parser(),
            remaining_source(arguments),
            model.model_with_rel_root_as_source_path(relativity_root_conf),
            arrangement=
            ArrangementPostAct(
                home_or_sds_contents=relativity_root_conf.populator_for_relativity_option_root(
                    DirContents([
                        File('1.txt', original_file_contents),
                        File('2.txt', original_file_contents),
                    ])
                ),
                symbols=symbol_table_with_lines_transformer
            ),
            expectation=
            Expectation(
                main_result=etc.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_references
            )
        )


class FileMatcherThatMatchesAnyFileWhosNameStartsWith(FileMatcher):
    @property
    def option_description(self) -> str:
        return 'Matches files beginning with ' + self._prefix_of_name_for_match

    def __init__(self, prefix_of_name_for_match: str):
        self._prefix_of_name_for_match = prefix_of_name_for_match

    def matches(self, path: pathlib.Path) -> bool:
        return path.name.startswith(self._prefix_of_name_for_match)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
