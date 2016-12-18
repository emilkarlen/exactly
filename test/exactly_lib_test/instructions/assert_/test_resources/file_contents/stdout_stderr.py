import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents import empty, equals, contains
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    InstructionTestConfigurationForEquals
from exactly_lib_test.instructions.test_resources.arrangements import ActResultProducerFromActResult
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulator
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.home_and_sds_test import Action
from exactly_lib_test.test_resources.parse import new_source2


class TestConfigurationForStdFile(InstructionTestConfigurationForEquals):
    def source_for(self,
                   argument_tail:
                   str, following_lines=()) -> SingleInstructionParserSource:
        return new_source2(argument_tail, following_lines)

    def arrangement_for_contents(self, actual_contents: str,
                                 post_sds_population_action: Action = Action(),
                                 ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=(self._act_result_producer(actual_contents)),
            post_sds_population_action=post_sds_population_action,
        )

    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator,
                                            post_sds_population_action: Action = Action(),
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
