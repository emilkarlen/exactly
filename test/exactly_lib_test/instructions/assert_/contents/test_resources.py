from exactly_lib.instructions.assert_ import contents as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contains as test_resources
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    InstructionTestConfigurationForEquals
from exactly_lib_test.instructions.test_resources.arrangements import ActEnvironment
from exactly_lib_test.test_resources.execution.home_and_sds_check import home_or_sds_populator as home_or_sds
from exactly_lib_test.test_resources.execution.home_and_sds_check.home_and_sds_utils import HomeAndSdsAction
from exactly_lib_test.test_resources.execution.home_and_sds_check.home_or_sds_populator import HomeOrSdsPopulator
from exactly_lib_test.test_resources.execution.sds_check import sds_populator
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.parse import remaining_source


class TestConfigurationForFile(InstructionTestConfigurationForEquals):
    FILE_NAME_REL_ACT = 'actual.txt'
    FILE_NAME_REL_CWD = '../actual.txt'

    def new_parser(self) -> InstructionParser:
        return sut.Parser()

    def source_for(self,
                   argument_tail: str,
                   following_lines=()) -> ParseSource:
        return remaining_source(self.FILE_NAME_REL_CWD + ' ' + argument_tail,
                                following_lines)

    def arrangement_for_contents(self, actual_contents: str,
                                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                 ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            sds_contents=self._populator_for_actual(actual_contents),
            post_sds_population_action=post_sds_population_action,
        )

    def arrangement_for_contents_from_fun(self,
                                          home_and_sds_2_str,
                                          home_or_sds_contents: home_or_sds.HomeOrSdsPopulator = home_or_sds.empty(),
                                          post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                          ) -> instruction_check.ArrangementPostAct:
        act_result_producer = _ActResultProducer(home_and_sds_2_str, self.FILE_NAME_REL_ACT)
        return instruction_check.ArrangementPostAct(
            act_result_producer=act_result_producer,
            home_or_sds_contents=home_or_sds_contents,
            post_sds_population_action=post_sds_population_action,
        )

    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator,
                                            post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                            ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            sds_contents=self._populator_for_actual(actual_contents),
            home_or_sds_contents=expected,
            post_sds_population_action=post_sds_population_action)

    def _populator_for_actual(self, actual_contents) -> sds_populator.SdsPopulator:
        return sds_populator.act_dir_contents(
            DirContents([
                File(self.FILE_NAME_REL_ACT, actual_contents)
            ]))


class _ActResultProducer(test_resources.ActResultProducer):
    def __init__(self, home_and_sds_2_str, file_name: str):
        self.home_and_sds_2_str = home_and_sds_2_str
        self.file_name = file_name

    def apply(self, act_environment: ActEnvironment) -> ActResult:
        actual_contents = self.home_and_sds_2_str(act_environment.home_and_sds)
        sds_pop = sds_populator.act_dir_contents(
            DirContents([
                File(self.file_name, actual_contents)
            ]))
        sds_pop.apply(act_environment.home_and_sds.sds)
        return ActResult()
