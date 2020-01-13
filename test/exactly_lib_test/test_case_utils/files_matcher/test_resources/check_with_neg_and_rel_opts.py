import unittest
from abc import ABC

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolsArrAndExpectSetup
from exactly_lib_test.test_case_file_structure.test_resources.ds_action import MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import \
    FilesMatcherArgumentsConstructor
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import ModelConstructorFromRelOptConf, \
    ModelConstructor
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation, ExecutionExpectation, \
    ParseExpectation
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import arrangement_w_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess, \
    expectation_type_config__non_is_success
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration, \
    SymbolsConfiguration, conf_rel_sds
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents

SOME_ACCEPTED_REL_OPT_CONFIGURATIONS = [
    conf_rel_sds(RelSdsOptionType.REL_ACT),
    conf_rel_sds(RelSdsOptionType.REL_TMP),
]


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
                 parser: Parser[FilesMatcherSdv]):

        self.put = put
        self.parser = parser

    def _check_(
            self,
            instruction_source: ParseSource,
            model: ModelConstructor,
            etc: ExpectationTypeConfigForNoneIsSuccess,
            main_result_for_positive_expectation: PassOrFail,
            root_dir_of_dir_contents: RelativityOptionConfiguration,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = '',
            following_symbols_setup: SymbolsArrAndExpectSetup = SymbolsArrAndExpectSetup.empty()):

        with self.put.subTest(case_name=test_case_name,
                              expectation_type=etc.expectation_type.name,
                              arguments=instruction_source.source_string):
            integration_check.CHECKER.check(
                self.put,
                instruction_source,
                model,
                arrangement_w_tcds(
                    pre_population_action=MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR,
                    tcds_contents=root_dir_of_dir_contents.populator_for_relativity_option_root(
                        contents_of_relativity_option_root
                    ),
                    symbols=_symbol_table_of(root_dir_of_dir_contents.symbols,
                                             following_symbols_setup),
                ),
                Expectation(
                    ParseExpectation(
                        symbol_references=following_symbols_setup.expected_references_assertion,
                    ),
                    ExecutionExpectation(
                        main_result=etc.main_result(main_result_for_positive_expectation),
                    ),
                ))

    def check_parsing_with_different_source_variants(
            self,
            make_instruction_arguments: FilesMatcherArgumentsConstructor,
            model_constructor: ModelConstructorFromRelOptConf,
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

                for source in equivalent_source_variants__with_source_check__for_expression_parser(
                        self.put,
                        Arguments(instruction_arguments)):
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
            model_constructor: ModelConstructorFromRelOptConf,
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
                model_constructor(root_dir_of_dir_contents),
                etc,
                main_result_for_positive_expectation,
                root_dir_of_dir_contents,
                contents_of_relativity_option_root,
                test_case_name,
                following_symbols_setup=following_symbols_setup)

    def check_rel_opt_variants_and_expectation_type_variants(
            self,
            make_instruction_arguments: FilesMatcherArgumentsConstructor,
            model_constructor: ModelConstructorFromRelOptConf,
            main_result_for_positive_expectation: PassOrFail,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = '',
            following_symbols_setup: SymbolsArrAndExpectSetup = SymbolsArrAndExpectSetup.empty()):

        for rel_opt_config in SOME_ACCEPTED_REL_OPT_CONFIGURATIONS:
            self.check_expectation_type_variants(
                make_instruction_arguments,
                model_constructor,
                main_result_for_positive_expectation,
                rel_opt_config,
                contents_of_relativity_option_root,
                test_case_name,
                following_symbols_setup=following_symbols_setup)


MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR = MkSubDirAndMakeItCurrentDirectory(
    SdsSubDirResolverFromSdsFun(lambda sds: sds.root_dir / 'test-cwd'))


def _symbol_table_of(sym_conf: SymbolsConfiguration,
                     symbols_setup: SymbolsArrAndExpectSetup,
                     ) -> SymbolTable:
    return symbols_setup.table_with_additional_entries(sym_conf.entries_for_arrangement())
