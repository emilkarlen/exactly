import unittest
from typing import List, Sequence, Callable

from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_system.logic.program.command import Command
from exactly_lib_test.instructions.configuration.actor.test_resources import file_in_hds_act_dir, CheckHelper, \
    exe_file_in_interpreter_default_relativity_dir, is_exe_file_command_for_source_file
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFileInterpreterActorForExecutableFile)


class TestFileInterpreterActorForExecutableFile(unittest.TestCase):
    helper = CheckHelper(actor_utils.FILE_INTERPRETER_NAME)

    def _check_both_single_and_multiple_line_source(
            self,
            instruction_argument_source_template: str,
            act_phase_source_lines: List[str],
            symbol_usages: ValueAssertion[Sequence[SymbolUsage]],
            expected_command: Callable[[TestCaseDs], ValueAssertion[Command]],
            hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
    ):
        self.helper.check_both_single_and_multiple_line_source(
            self,
            instruction_argument_source_template,
            act_phase_source_lines=act_phase_source_lines,
            symbol_usages=symbol_usages,
            expected_command=expected_command,
            hds_contents=hds_contents)

    def test_single_command(self):
        interpreter_exe_file_name = 'interpreter'
        src_file_name = 'file.src'

        self._check_both_single_and_multiple_line_source(
            '= {actor_option} interpreter',
            [src_file_name],
            asrt.is_empty_sequence,
            is_exe_file_command_for_source_file(interpreter_exe_file_name,
                                                src_file_name,
                                                []),
            hds_contents=hds_populators.multiple([
                exe_file_in_interpreter_default_relativity_dir(interpreter_exe_file_name),
                file_in_hds_act_dir(src_file_name),
            ]),
        )

    def test_command_with_arguments(self):
        interpreter_exe_file_name = 'interpreter'
        src_file_name = 'file.src'

        self._check_both_single_and_multiple_line_source(
            ' = {actor_option}   interpreter   arg1     -arg2   ',
            ['file.src'],
            asrt.is_empty_sequence,
            is_exe_file_command_for_source_file(interpreter_exe_file_name,
                                                src_file_name,
                                                ['arg1',
                                                 '-arg2']),
            hds_contents=hds_populators.multiple([
                exe_file_in_interpreter_default_relativity_dir(interpreter_exe_file_name),
                file_in_hds_act_dir(src_file_name),
            ]),
        )

    def test_quoting(self):
        interpreter_exe_file_name = 'interpreter with space'
        src_file_name = 'file.src'

        self._check_both_single_and_multiple_line_source(
            "= {actor_option} 'interpreter with space' arg2 \"arg 3\"",
            [src_file_name],
            asrt.is_empty_sequence,
            is_exe_file_command_for_source_file(
                interpreter_exe_file_name,
                src_file_name,
                ['arg2', 'arg 3']),
            hds_contents=hds_populators.multiple([
                exe_file_in_interpreter_default_relativity_dir(interpreter_exe_file_name),
                file_in_hds_act_dir(src_file_name),
            ]),
        )
