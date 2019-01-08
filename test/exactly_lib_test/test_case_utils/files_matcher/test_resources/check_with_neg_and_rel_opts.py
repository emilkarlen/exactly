import unittest

from abc import ABC
from typing import List, Callable

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.files_matcher import FilesMatcherResolver
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolsArrAndExpectSetup
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    FilesMatcherArgumentsConstructor
from exactly_lib_test.test_case_utils.files_matcher.test_resources.integration_check import Expectation, Model
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess, \
    expectation_type_config__non_is_success
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration, \
    SymbolsConfiguration, conf_rel_sds
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

SOME_ACCEPTED_REL_OPT_CONFIGURATIONS = [
    conf_rel_sds(RelSdsOptionType.REL_ACT),
    conf_rel_sds(RelSdsOptionType.REL_TMP),
]


def model_with_rel_root_as_source_path(root_dir_of_dir_contents: RelativityOptionConfiguration) -> Model:
    return Model(root_dir_of_dir_contents.file_ref_resolver_for())


def model_with_source_path_as_sub_dir_of_rel_root(subdir: str) -> Callable[[RelativityOptionConfiguration], Model]:
    def ret_val(root_dir_of_dir_contents: RelativityOptionConfiguration) -> Model:
        return Model(root_dir_of_dir_contents.file_ref_resolver_for(subdir))

    return ret_val


class FilesMatcherArgumentsConstructorWithTemplateStringBase(FilesMatcherArgumentsConstructor, ABC):
    def __init__(self, matcher_argument_template: str):
        self.matcher_argument_template = matcher_argument_template


class MatcherChecker:
    """
    Methods for checking an instruction with arguments for
    negation.
    """

    def __init__(self,
                 put: unittest.TestCase,
                 parser: Parser[FilesMatcherResolver]):

        self.put = put
        self.parser = parser

    def _check_(
            self,
            instruction_source: ParseSource,
            model: Model,
            etc: ExpectationTypeConfigForNoneIsSuccess,
            main_result_for_positive_expectation: PassOrFail,
            root_dir_of_dir_contents: RelativityOptionConfiguration,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = '',
            following_symbols_setup: SymbolsArrAndExpectSetup = SymbolsArrAndExpectSetup.empty()):

        with self.put.subTest(case_name=test_case_name,
                              expectation_type=etc.expectation_type.name,
                              arguments=instruction_source.source_string):
            integration_check.check(
                self.put,
                self.parser,
                instruction_source,
                model,
                ArrangementPostAct(
                    pre_contents_population_action=MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR,
                    home_or_sds_contents=root_dir_of_dir_contents.populator_for_relativity_option_root(
                        contents_of_relativity_option_root
                    ),
                    symbols=_symbol_table_of(root_dir_of_dir_contents.symbols,
                                             following_symbols_setup),
                ),
                Expectation(
                    main_result=etc.main_result(main_result_for_positive_expectation),
                    symbol_usages=following_symbols_setup.expected_references_assertion,
                ))

    def check_parsing_with_different_source_variants(
            self,
            make_instruction_arguments: FilesMatcherArgumentsConstructor,
            model_constructor: Callable[[RelativityOptionConfiguration], Model],
            default_relativity: RelOptionType,
            non_default_relativity: RelOptionType,
            main_result_for_positive_expectation: PassOrFail,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            following_symbols_setup: SymbolsArrAndExpectSetup = SymbolsArrAndExpectSetup.empty()):

        rel_opt_configs = [
            rel_opt_conf.default_conf_rel_any(default_relativity),
            rel_opt_conf.conf_rel_any(non_default_relativity),
        ]

        for rel_opt_config in rel_opt_configs:
            for expectation_type_of_test_case in ExpectationType:
                etc = expectation_type_config__non_is_success(expectation_type_of_test_case)
                instruction_arguments = make_instruction_arguments.apply(etc)

                for source in equivalent_source_variants__with_source_check(self.put, instruction_arguments):
                    self._check_(
                        source,
                        model_constructor(rel_opt_config),
                        etc,
                        main_result_for_positive_expectation,
                        rel_opt_config,
                        contents_of_relativity_option_root,
                        following_symbols_setup=following_symbols_setup)

    def check_expectation_type_variants(
            self,
            make_instruction_arguments: FilesMatcherArgumentsConstructor,
            model: Model,
            main_result_for_positive_expectation: PassOrFail,
            root_dir_of_dir_contents: RelativityOptionConfiguration,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = '',
            following_symbols_setup: SymbolsArrAndExpectSetup = SymbolsArrAndExpectSetup.empty()):

        for expectation_type_of_test_case in ExpectationType:
            etc = expectation_type_config__non_is_success(expectation_type_of_test_case)
            instruction_arguments = make_instruction_arguments.apply(etc)
            self._check_(
                remaining_source(instruction_arguments),
                model,
                etc,
                main_result_for_positive_expectation,
                root_dir_of_dir_contents,
                contents_of_relativity_option_root,
                test_case_name,
                following_symbols_setup=following_symbols_setup)

    def check_rel_opt_variants_and_expectation_type_variants(
            self,
            make_instruction_arguments: FilesMatcherArgumentsConstructor,
            model_constructor: Callable[[RelativityOptionConfiguration], Model],
            main_result_for_positive_expectation: PassOrFail,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = '',
            following_symbols_setup: SymbolsArrAndExpectSetup = SymbolsArrAndExpectSetup.empty()):

        for rel_opt_config in SOME_ACCEPTED_REL_OPT_CONFIGURATIONS:
            self.check_expectation_type_variants(
                make_instruction_arguments,
                model_constructor(rel_opt_config),
                main_result_for_positive_expectation,
                rel_opt_config,
                contents_of_relativity_option_root,
                test_case_name,
                following_symbols_setup=following_symbols_setup)

    def check_rel_opt_variants_with_same_result_for_every_expectation_type(
            self,
            make_instruction_arguments: FilesMatcherArgumentsConstructor,
            main_result: ValueAssertion,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            following_symbols_setup: SymbolsArrAndExpectSetup = SymbolsArrAndExpectSetup.empty()):

        for rel_opt_config in SOME_ACCEPTED_REL_OPT_CONFIGURATIONS:

            for expectation_type_of_test_case in ExpectationType:
                etc = expectation_type_config__non_is_success(expectation_type_of_test_case)
                instruction_arguments = make_instruction_arguments.apply(etc)
                instruction_source = remaining_source(instruction_arguments)

                with self.put.subTest(expectation_type=etc.expectation_type.name,
                                      arguments=instruction_arguments):
                    integration_check.check(
                        self.put,
                        self.parser,
                        instruction_source,
                        Model(rel_opt_config.file_ref_resolver_for()),
                        ArrangementPostAct(
                            pre_contents_population_action=MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR,
                            home_or_sds_contents=rel_opt_config.populator_for_relativity_option_root(
                                contents_of_relativity_option_root
                            ),
                            symbols=_symbol_table_of(rel_opt_config.symbols,
                                                     following_symbols_setup),
                        ),
                        Expectation(
                            main_result=main_result,
                            symbol_usages=asrt.matches_sequence(
                                rel_opt_config.symbols.usage_expectation_assertions() +
                                following_symbols_setup.expected_references_list
                            )
                        ))

    def check_rel_opt_variants(
            self,
            make_instruction_arguments: FilesMatcherArgumentsConstructor,
            model_constructor: Callable[[RelativityOptionConfiguration], Model],
            main_result_for_positive_expectation: PassOrFail,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = '',
            following_symbols_setup: SymbolsArrAndExpectSetup = SymbolsArrAndExpectSetup.empty()):

        for rel_opt_config in SOME_ACCEPTED_REL_OPT_CONFIGURATIONS:
            etc = expectation_type_config__non_is_success(ExpectationType.POSITIVE)
            instruction_arguments = make_instruction_arguments.apply(etc)
            self._check_(
                remaining_source(instruction_arguments),
                model_constructor(rel_opt_config),
                etc,
                main_result_for_positive_expectation,
                rel_opt_config,
                contents_of_relativity_option_root,
                test_case_name,
                following_symbols_setup=following_symbols_setup)

    def check_multiple_cases_with_rel_opt_variants_and_expectation_type_variants(
            self,
            test_cases_with_name_and_dir_contents: List[NameAndValue[DirContents]],
            make_instruction_arguments: FilesMatcherArgumentsConstructor,
            model_constructor: Callable[[RelativityOptionConfiguration], Model],
            main_result_for_positive_expectation: PassOrFail,
            following_symbols_setup: SymbolsArrAndExpectSetup = SymbolsArrAndExpectSetup.empty()):

        for case in test_cases_with_name_and_dir_contents:
            self.check_rel_opt_variants_and_expectation_type_variants(
                make_instruction_arguments,
                model_constructor,
                main_result_for_positive_expectation,
                contents_of_relativity_option_root=case.value,
                test_case_name=case.name,
                following_symbols_setup=following_symbols_setup)


MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR = MkSubDirAndMakeItCurrentDirectory(
    SdsSubDirResolverFromSdsFun(lambda sds: sds.root_dir / 'test-cwd'))


def _symbol_table_of(sym_conf: SymbolsConfiguration,
                     symbols_setup: SymbolsArrAndExpectSetup,
                     ) -> SymbolTable:
    return symbols_setup.table_with_additional_entries(sym_conf.entries_for_arrangement())
