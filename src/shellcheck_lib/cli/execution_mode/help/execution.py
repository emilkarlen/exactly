from shellcheck_lib.cli.instruction_setup import InstructionsSetup
from shellcheck_lib.cli import main_program
from shellcheck_lib.execution import phase_step


class PrintInstructionsPerPhase:
    def __init__(self,
                 output: main_program.StdOutputFiles):
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
        self._std.out.writeln(phase_name)
        for instruction_name, instruction_setup in instruction_set:
            self._std.out.writeln(instruction_name + ' ' + instruction_setup.description.single_line_description)
