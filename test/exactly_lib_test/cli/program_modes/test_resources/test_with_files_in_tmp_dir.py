import unittest

from typing import List

from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib_test.cli.program_modes.test_resources import main_program_execution
from exactly_lib_test.cli.program_modes.test_resources.main_program_execution import MainProgramConfig, \
    capture_output_from_main_program, main_program_from_config
from exactly_lib_test.cli.program_modes.test_resources.test_case_setup import test_case_definition_for
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Arrangement:
    def __init__(self,
                 main_program_config: MainProgramConfig =
                 main_program_execution.main_program_config(test_case_definition_for(InstructionsSetup())),

                 cwd_contents: DirContents = DirContents([])):
        self.main_program_config = main_program_config
        self.cwd_contents = cwd_contents


def check(put: unittest.TestCase,
          command_line_arguments: List[str],
          arrangement: Arrangement,
          expectation: ValueAssertion[SubProcessResult]):
    # ARRANGE #
    main_program = main_program_from_config(arrangement.main_program_config)
    with tmp_dir_as_cwd(arrangement.cwd_contents) as cwd:
        # ACT #
        result = capture_output_from_main_program(command_line_arguments,
                                                  main_program)
        # ASSERT #
        expectation.apply_without_message(put, result)
