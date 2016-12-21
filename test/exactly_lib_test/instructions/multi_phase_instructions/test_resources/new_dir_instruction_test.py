import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    RelativityOptionConfigurationForRelSdsBase
from exactly_lib_test.instructions.multi_phase_instructions import new_dir
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from exactly_lib_test.instructions.test_resources.check_description import suite_for_documentation_instance
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.execution.utils import HomeAndSdsActionFromSdsAction
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file
from exactly_lib_test.test_resources.parse import new_source2
from exactly_lib_test.test_resources.value_assertions.sds_contents_check import SubDirOfSdsContainsExactly


class Configuration(ConfigurationBase):
    def expect_failure_to_create_dir(self):
        raise NotImplementedError()


class TestCaseBase(unittest.TestCase):
    def __init__(self,
                 conf: Configuration,
                 relativity_option: RelativityOptionConfigurationForRelSdsBase):
        super().__init__()
        self.relativity_option = relativity_option
        self.conf = conf

    def _source(self, argument_template: str) -> SingleInstructionParserSource:
        return new_source2(argument_template.format(relativity_option=self.relativity_option.option_string))

    def _arrangement_with_sub_dir_of_act_as_cwd(
            self,
            sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty()):
        return self.conf.arrangement(
            sds_contents_before_main=sds_contents_before_main,
            pre_contents_population_action=HomeAndSdsActionFromSdsAction(new_dir.SETUP_CWD_ACTION))

    def shortDescription(self):
        return '{}\n / {}\n / {}'.format(type(self),
                                         type(self.conf),
                                         type(self.relativity_option))


class TestCreationOfDirectory(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            self._source('{relativity_option} first-component/second-component'),
            self._arrangement_with_sub_dir_of_act_as_cwd(),
            self.conf.expect_success_and_side_effects_on_files(
                main_side_effects_on_files=SubDirOfSdsContainsExactly(
                    self.relativity_option.root_dir__sds,
                    DirContents([
                        Dir('first-component', [
                            empty_dir('second-component')
                        ])
                    ])))
        )


class TestArgumentExistsAsNonDirectory(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            self._source('{relativity_option} file'),
            self._arrangement_with_sub_dir_of_act_as_cwd(
                sds_contents_before_main=self.relativity_option.populator_for_relativity_option_root__sds(
                    DirContents([
                        empty_file('file')
                    ]))),
            self.conf.expect_failure_to_create_dir()
        )


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
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
