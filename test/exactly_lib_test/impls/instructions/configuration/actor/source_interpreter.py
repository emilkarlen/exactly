import unittest
from typing import Sequence, Callable

from exactly_lib.impls.instructions.configuration.utils import actor_utils
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib_test.impls.instructions.configuration.actor.test_resources import CheckHelper, \
    exe_file_in_interpreter_default_relativity_dir, is_exe_file_command_for_source
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSourceInterpreterActorForExecutableFile)


class TestSourceInterpreterActorForExecutableFile(unittest.TestCase):
    helper = CheckHelper(actor_utils.SOURCE_INTERPRETER_NAME)

    def _check_both_single_and_multiple_line_source(
            self,
            instruction_argument_source_template: str,
            symbol_usages: ValueAssertion[Sequence[SymbolUsage]],
            expected_command: Callable[[TestCaseDs], ValueAssertion[Command]],
            hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
    ):
        self.helper.check_both_single_and_multiple_line_source(
            self,
            instruction_argument_source_template,
            act_phase_source_lines=['this is act phase source code that is not used in the test'],
            symbol_usages=symbol_usages,
            expected_command=expected_command,
            hds_contents=hds_contents,
        )

    def test_single_command(self):
        interpreter_exe_file_name = 'executable'

        self._check_both_single_and_multiple_line_source(
            ' = {actor_option} executable',
            asrt.is_empty_sequence,
            is_exe_file_command_for_source(interpreter_exe_file_name,
                                           []),
            exe_file_in_interpreter_default_relativity_dir(interpreter_exe_file_name),
        )

    def test_command_with_arguments(self):
        interpreter_exe_file_name = 'executable'

        self._check_both_single_and_multiple_line_source(
            '=  {actor_option} executable arg1 -arg2',
            asrt.is_empty_sequence,
            is_exe_file_command_for_source(interpreter_exe_file_name,
                                           ['arg1', '-arg2']),
            exe_file_in_interpreter_default_relativity_dir(interpreter_exe_file_name),
        )

    def test_quoting(self):
        interpreter_exe_file_name = 'executable with space'
        self._check_both_single_and_multiple_line_source(
            "= {actor_option} 'executable with space' arg2 \"arg 3\"",
            asrt.is_empty_sequence,
            is_exe_file_command_for_source(interpreter_exe_file_name,
                                           ['arg2', 'arg 3']),
            exe_file_in_interpreter_default_relativity_dir(interpreter_exe_file_name),
        )
