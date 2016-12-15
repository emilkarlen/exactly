import unittest

from exactly_lib.instructions.assert_ import contents as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionParser
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contains as test_resources
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestConfiguration
from exactly_lib_test.instructions.test_resources.arrangements import ActEnvironment
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.parse import new_source2


class _TestConfiguration(TestConfiguration):
    FILE_NAME = 'actual.txt'

    def new_parser(self) -> SingleInstructionParser:
        return sut.Parser()

    def source_for(self, argument_tail: str) -> SingleInstructionParserSource:
        return new_source2(self.FILE_NAME + ' ' + argument_tail)

    def arrangement_for_contents(self, actual_contents: str) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(sds_contents=sds_populator.act_dir_contents(
            DirContents([
                File(self.FILE_NAME, actual_contents)
            ])))

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        act_result_producer = _ActResultProducer(home_and_sds_2_str, self.FILE_NAME)
        return instruction_check.ArrangementPostAct(act_result_producer=act_result_producer)


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


def suite() -> unittest.TestSuite:
    return test_resources.suite_for(_TestConfiguration())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
