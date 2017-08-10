from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.assert_.test_resources.instruction_with_negation_argument import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.assert_.test_resources.instruction_with_negation_argument import PassOrFail
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    MkSubDirAndMakeItCurrentDirectory


class InstructionArgumentsVariantConstructor:
    """
    Constructs the instruction argument for a given negation-option config
    and rel-opt config.
    """

    def __init__(self, instruction_argument_template: str):
        self.instruction_argument_template = instruction_argument_template

    def apply(self,
              etc: ExpectationTypeConfig,
              rel_opt_config: RelativityOptionConfiguration,
              ) -> str:
        raise NotImplementedError('abstract method')


class TestCaseBaseWithParser(instruction_check.TestCaseBase):
    def _parser(self) -> InstructionParser:
        raise NotImplementedError('abstract method')

    def _accepted_rel_opt_configurations(self) -> list:
        raise NotImplementedError('abstract method')

    def _check_(
            self,
            instruction_source: ParseSource,
            etc: ExpectationTypeConfig,
            main_result_for_positive_expectation: PassOrFail,
            rel_opt_config: RelativityOptionConfiguration,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = ''):

        with self.subTest(case_name=test_case_name,
                          expectation_type=str(etc.expectation_type),
                          arguments=instruction_source.source_string):
            self._check(self._parser(),
                        instruction_source,
                        ArrangementPostAct(
                            pre_contents_population_action=MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR,
                            home_or_sds_contents=rel_opt_config.populator_for_relativity_option_root(
                                contents_of_relativity_option_root
                            ),
                            symbols=rel_opt_config.symbols.in_arrangement(),
                        ),
                        Expectation(
                            main_result=etc.main_result(main_result_for_positive_expectation),
                            symbol_usages=rel_opt_config.symbols.usages_expectation(),
                        ))

    def _check_parsing_with_different_source_variants(
            self,
            make_instruction_arguments: InstructionArgumentsVariantConstructor,
            default_relativity: RelOptionType,
            non_default_relativity: RelOptionType,
            main_result_for_positive_expectation: PassOrFail,
            contents_of_relativity_option_root: DirContents = empty_dir_contents()):

        rel_opt_configs = [
            rel_opt_conf.default_conf_rel_any(default_relativity),
            rel_opt_conf.conf_rel_any(non_default_relativity),
        ]

        for rel_opt_config in rel_opt_configs:
            for expectation_type_of_test_case in ExpectationType:
                etc = ExpectationTypeConfig(expectation_type_of_test_case)
                instruction_arguments = make_instruction_arguments.apply(etc, rel_opt_config)

                for source in equivalent_source_variants__with_source_check(self, instruction_arguments):
                    self._check_(
                        source,
                        etc,
                        main_result_for_positive_expectation,
                        rel_opt_config,
                        contents_of_relativity_option_root)

    def _check_with_expectation_type_variants(
            self,
            make_instruction_arguments: InstructionArgumentsVariantConstructor,
            main_result_for_positive_expectation: PassOrFail,
            rel_opt_config: RelativityOptionConfiguration,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = ''):

        for expectation_type_of_test_case in ExpectationType:
            etc = ExpectationTypeConfig(expectation_type_of_test_case)
            instruction_arguments = make_instruction_arguments.apply(etc, rel_opt_config)
            self._check_(
                remaining_source(instruction_arguments),
                etc,
                main_result_for_positive_expectation,
                rel_opt_config,
                contents_of_relativity_option_root,
                test_case_name)

    def _check_with_rel_opt_variants_and_expectation_type_variants(
            self,
            make_instruction_arguments: InstructionArgumentsVariantConstructor,
            main_result_for_positive_expectation: PassOrFail,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = ''):

        for rel_opt_config in self._accepted_rel_opt_configurations():
            self._check_with_expectation_type_variants(
                make_instruction_arguments,
                main_result_for_positive_expectation,
                rel_opt_config,
                contents_of_relativity_option_root,
                test_case_name)

    def _check_with_rel_opt_variants(
            self,
            make_instruction_arguments: InstructionArgumentsVariantConstructor,
            main_result_for_positive_expectation: PassOrFail,
            contents_of_relativity_option_root: DirContents = empty_dir_contents(),
            test_case_name: str = ''):

        for rel_opt_config in self._accepted_rel_opt_configurations():
            etc = ExpectationTypeConfig(ExpectationType.POSITIVE)
            instruction_arguments = make_instruction_arguments.apply(etc, rel_opt_config)
            self._check_(
                remaining_source(instruction_arguments),
                etc,
                main_result_for_positive_expectation,
                rel_opt_config,
                contents_of_relativity_option_root,
                test_case_name)

    def _run_test_cases_with_rel_opt_root_dir_contents_and_expectation_type_variants(
            self,
            test_cases_with_name_and_dir_contents: list,
            make_instruction_arguments: InstructionArgumentsVariantConstructor,
            main_result_for_positive_expectation: PassOrFail):

        for case in test_cases_with_name_and_dir_contents:
            self._check_with_rel_opt_variants_and_expectation_type_variants(
                make_instruction_arguments,
                main_result_for_positive_expectation,
                contents_of_relativity_option_root=case.value,
                test_case_name=case.name)


MAKE_CWD_OUTSIDE_OF_EVERY_REL_OPT_DIR = MkSubDirAndMakeItCurrentDirectory(
    SdsSubDirResolverFromSdsFun(lambda sds: sds.root_dir / 'test-cwd'))
