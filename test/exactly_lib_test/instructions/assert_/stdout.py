import unittest

import exactly_lib_test.instructions.assert_.test_resources.file_contents.stdout_stderr
from exactly_lib.instructions.assert_ import stdout as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.contains import \
    ActResultProducerFromHomeAndSds2Str
from exactly_lib_test.instructions.assert_.test_resources.file_contents.stdout_stderr import TestConfigurationForStdFile
from exactly_lib_test.instructions.test_resources.arrangements import ActEnvironment
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.execution import home_or_sds_populator as home_or_sds
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.home_and_sds_test import HomeAndSdsAction


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        exactly_lib_test.instructions.assert_.test_resources.file_contents.stdout_stderr.suite_for(
            TestConfigurationForStdout()),
        suite_for_instruction_documentation(sut.setup_for_stdout('instruction name').documentation),
    ])


class ActResultProducerForStdout(ActResultProducerFromHomeAndSds2Str):
    def apply(self, act_environment: ActEnvironment) -> ActResult:
        return ActResult(stdout_contents=self.home_and_sds_2_str(act_environment.home_and_sds))


class TestConfigurationForStdout(TestConfigurationForStdFile):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str,
                                          home_or_sds_contents: home_or_sds.HomeOrSdsPopulator = home_or_sds.empty(),
                                          post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                          ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=ActResultProducerForStdout(home_and_sds_2_str),
            home_or_sds_contents=home_or_sds_contents,
            post_sds_population_action=post_sds_population_action,
        )

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        return ActResult(stdout_contents=contents_of_tested_file)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
