import unittest
from typing import Callable

from exactly_lib.instructions.assert_ import stdout as sut
from exactly_lib.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources import stdout_stderr
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr import ProgramOutputInstructionConfiguration
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.configuration_for_contents_of_act_result import \
    TestConfigurationForStdFile
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.utils import \
    ActResultProducerFromTcds2Str
from exactly_lib_test.tcfs.test_resources import tcds_populators as tcds
from exactly_lib_test.test_case.test_resources.act_result import ActEnvironment
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        stdout_stderr.suite_for(TestConfigurationForStdout(),
                                ProgramOutputInstructionConfigurationForStdout()),
        suite_for_instruction_documentation(sut.setup_for_stdout('instruction name').documentation),
    ])


class ActResultProducerForStdout(ActResultProducerFromTcds2Str):
    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        return SubProcessResult(stdout=self.tcds_2_str(act_environment.tcds))


class TestConfigurationForStdout(TestConfigurationForStdFile):
    def new_parser(self) -> InstructionParser:
        return sut.parser('the-instruction-name')

    def arrangement_for_contents_from_fun(self,
                                          tcds_2_str: Callable[[TestCaseDs], str],
                                          tcds_contents: tcds.TcdsPopulator = tcds.empty(),
                                          post_sds_population_action: TcdsAction = TcdsAction(),
                                          symbols: SymbolTable = None,
                                          ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=ActResultProducerForStdout(tcds_2_str),
            tcds_contents=tcds_contents,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def act_result(self, contents_of_tested_file: str) -> SubProcessResult:
        return SubProcessResult(stdout=contents_of_tested_file)


class ProgramOutputInstructionConfigurationForStdout(ProgramOutputInstructionConfiguration):
    def output_file(self) -> ProcOutputFile:
        return ProcOutputFile.STDOUT

    def parser(self) -> AssertPhaseInstructionParser:
        return sut.parser('the-instruction-name')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
