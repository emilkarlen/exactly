import unittest

from exactly_lib.impls.instructions.assert_.process_output import stderr as sut
from exactly_lib.impls.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err import test_resources
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err.test_resources.configuration_for_contents_of_act_result import \
    TestConfigurationForStdFile
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err.test_resources.program_output import \
    ProgramOutputInstructionConfiguration
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err.test_resources.utils import \
    ActResultProducerFromTcds2Str
from exactly_lib_test.test_case.test_resources.act_result import ActEnvironment
from exactly_lib_test.test_resources.process import SubProcessResult


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources.suite_for(TestConfigurationForStderr(),
                                 ProgramOutputInstructionConfigurationForStderr()),
        suite_for_instruction_documentation(sut.setup_for_stderr('instruction name').documentation),
    ])


class ActResultProducerForStderr(ActResultProducerFromTcds2Str):
    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        return SubProcessResult(stderr=self.tcds_2_str(act_environment.tcds))


class TestConfigurationForStderr(TestConfigurationForStdFile):
    def new_parser(self) -> InstructionParser:
        return sut.parser('the-instruction-name')

    def act_result(self, contents_of_tested_file: str) -> SubProcessResult:
        return SubProcessResult(stderr=contents_of_tested_file)


class ProgramOutputInstructionConfigurationForStderr(ProgramOutputInstructionConfiguration):
    def output_file(self) -> ProcOutputFile:
        return ProcOutputFile.STDERR

    def parser(self) -> AssertPhaseInstructionParser:
        return sut.parser('the-instruction-name')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
