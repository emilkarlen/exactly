import unittest

from exactly_lib.instructions.assert_ import stderr as sut
from exactly_lib.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources import stdout_stderr
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.configuration_for_contents_of_act_result import \
    TestConfigurationForStdFile
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    ProgramOutputInstructionConfiguration
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.utils import \
    ActResultProducerFromHomeAndSds2Str
from exactly_lib_test.instructions.test_resources.arrangements import ActEnvironment
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import \
    home_and_sds_populators as home_or_sds
from exactly_lib_test.test_resources.execution.utils import ProcessResult
from exactly_lib_test.test_resources.programs.py_programs import single_line_pgm_that_prints_to_no_new_line
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        stdout_stderr.suite_without_program_output_DURING_DEVELOPMENT(TestConfigurationForStderr(),
                                                                      ProgramOutputInstructionConfigurationForStderr()),
        suite_for_instruction_documentation(sut.setup_for_stderr('instruction name').documentation),
    ])


class ActResultProducerForStderr(ActResultProducerFromHomeAndSds2Str):
    def apply(self, act_environment: ActEnvironment) -> ProcessResult:
        return ProcessResult(stderr_contents=self.home_and_sds_2_str(act_environment.home_and_sds))


class TestConfigurationForStderr(TestConfigurationForStdFile):
    def new_parser(self) -> InstructionParser:
        return sut.parser('the-instruction-name')

    def arrangement_for_contents_from_fun(self,
                                          home_and_sds_2_str,
                                          home_or_sds_contents: home_or_sds.HomeOrSdsPopulator = home_or_sds.empty(),
                                          post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                          symbols: SymbolTable = None,
                                          ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=ActResultProducerForStderr(home_and_sds_2_str),
            home_or_sds_contents=home_or_sds_contents,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def act_result(self, contents_of_tested_file: str) -> ProcessResult:
        return ProcessResult(stderr_contents=contents_of_tested_file)


class ProgramOutputInstructionConfigurationForStderr(ProgramOutputInstructionConfiguration):

    def parser(self) -> AssertPhaseInstructionParser:
        return sut.parser('the-instruction-name')

    def py_source_for_print(self, output: str) -> str:
        return single_line_pgm_that_prints_to_no_new_line('stderr', output)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
