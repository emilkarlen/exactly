import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_documentation_instance
from exactly_lib_test.instructions.multi_phase import new_dir
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.section_document.test_resources.parse_source import source4
from exactly_lib_test.test_case_file_structure.test_resources import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    SubDirOfSdsContainsExactly
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_utils.test_resources.relativity_options import \
    RelativityOptionConfigurationForRelSds
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir, Dir, empty_file
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsActionFromSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Configuration(ConfigurationBase):
    def expect_failure_to_create_dir(self,
                                     symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        raise NotImplementedError()


def suite_for(conf: Configuration) -> unittest.TestSuite:
    test_cases = [
        TestCreationOfDirectory,
        TestArgumentExistsAsNonDirectory,
    ]
    suites = []
    for test_case in test_cases:
        for rel_opt in new_dir.RELATIVITY_OPTIONS:
            suites.append(test_case(conf, rel_opt))
    suites.append(suite_for_documentation_instance(conf.documentation()))
    return unittest.TestSuite(suites)


class TestCaseBase(unittest.TestCase):
    def __init__(self,
                 conf: Configuration,
                 relativity_option: RelativityOptionConfigurationForRelSds):
        super().__init__()
        self.relativity_option = relativity_option
        self.conf = conf

    def _source(self, argument_template: str) -> ParseSource:
        return source4(argument_template.format(relativity_option=self.relativity_option.option_argument))

    def _instruction_argument(self, argument_template: str) -> str:
        return argument_template.format(relativity_option=self.relativity_option.option_argument)

    def _arrangement_with_cwd_as_non_of_the_relativity_root_dirs(
            self,
            sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty()):
        return self.conf.arrangement(
            sds_contents_before_main=sds_contents_before_main,
            pre_contents_population_action=HomeAndSdsActionFromSdsAction(new_dir.SETUP_CWD_ACTION),
            symbols=self.relativity_option.symbols.in_arrangement())

    def shortDescription(self):
        return '{}\n / {}\n / {}'.format(type(self),
                                         type(self.conf),
                                         type(self.relativity_option))


class TestCreationOfDirectory(TestCaseBase):
    def runTest(self):
        instruction_argument_template = '{relativity_option} first-component/second-component'
        instruction_argument = self._instruction_argument(instruction_argument_template)
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self.conf.run_test(
                self,
                source,
                self._arrangement_with_cwd_as_non_of_the_relativity_root_dirs(),
                self.conf.expect_success(
                    main_side_effects_on_sds=SubDirOfSdsContainsExactly(
                        self.relativity_option.root_dir__sds,
                        DirContents([
                            Dir('first-component', [
                                empty_dir('second-component')
                            ])
                        ])),
                    symbol_usages=self.relativity_option.symbols.usages_expectation(),
                )
            )


class TestArgumentExistsAsNonDirectory(TestCaseBase):
    def runTest(self):
        instruction_argument_template = '{relativity_option} file'
        instruction_argument = self._instruction_argument(instruction_argument_template)
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self.conf.run_test(
                self,
                source,
                self._arrangement_with_cwd_as_non_of_the_relativity_root_dirs(
                    sds_contents_before_main=self.relativity_option.populator_for_relativity_option_root__sds(
                        DirContents([
                            empty_file('file')
                        ]))),
                self.conf.expect_failure_to_create_dir(
                    symbol_usages=self.relativity_option.symbols.usages_expectation(),
                )
            )
