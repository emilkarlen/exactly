import unittest

from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents import empty, equals, contains
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    InstructionTestConfigurationForEquals
from exactly_lib_test.instructions.test_resources.arrangements import ActResultProducerFromActResult
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_or_sds_populator import \
    HomeOrSdsPopulator
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction


class TestConfigurationForStdFile(InstructionTestConfigurationForEquals):
    def first_line_argument(self, argument_tail: str) -> str:
        return argument_tail

    def arrangement_for_contents(self, actual_contents: str,
                                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                 ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=(self._act_result_producer(actual_contents)),
            post_sds_population_action=post_sds_population_action,
        )

    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator,
                                            post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                            ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=(self._act_result_producer(actual_contents)),
            home_or_sds_contents=expected,
            post_sds_population_action=post_sds_population_action,
        )

    def act_result(self, contents_of_tested_file: str) -> ActResult:
        raise NotImplementedError()

    def _act_result_producer(self, contents_of_tested_file: str) -> instruction_check.ActResultProducer:
        act_result = self.act_result(contents_of_tested_file)
        return ActResultProducerFromActResult(act_result)


def suite_for(configuration: InstructionTestConfigurationForEquals) -> unittest.TestSuite:
    return unittest.TestSuite([
        empty.suite_for(configuration),
        equals.suite_for(configuration),
        contains.suite_for(configuration),

    ])
