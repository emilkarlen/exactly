import os

from shellcheck_lib.default.execution_mode.test_case.instruction_setup2 import InstructionsSetup
from shellcheck_lib.execution import phase_step
from shellcheck_lib.general.output import StdOutputFiles


class PrintInstructionsPerPhase:
    def __init__(self,
                 output: StdOutputFiles):
        self._std = output

    def apply(self, instruction_setup: InstructionsSetup):
        self._print_phase(phase_step.ANONYMOUS, instruction_setup.config_instruction_set)
        self._print_phase(phase_step.SETUP, instruction_setup.setup_instruction_set)
        self._print_phase(phase_step.ASSERT, instruction_setup.assert_instruction_set)
        self._print_phase(phase_step.CLEANUP, instruction_setup.cleanup_instruction_set)

    def _print_phase(self,
                     phase_name: str,
                     instruction_set: dict):
        if not instruction_set:
            return
        self._writeln(phase_name)
        for instruction_name, instruction_setup in instruction_set.items():
            self._writeln(instruction_name + ' : ' + instruction_setup.description.single_line_description)

    def _writeln(self, s: str):
        self._std.out.write(s)
        self._std.out.write(os.linesep)
