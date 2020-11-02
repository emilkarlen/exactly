import sys
import unittest

from exactly_lib.impls.instructions.configuration.utils import actor_utils
from exactly_lib.impls.os_services import os_services_access
from exactly_lib_test.appl_env.test_resources.command_executors import CommandExecutorThatRecordsArguments
from exactly_lib_test.impls.instructions.configuration.actor.test_resources import Arrangement, Expectation, \
    check_actor_execution, ExecutedCommandAssertion
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_path
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCommandLineActorForActPhaseContentsOfExecutableFile)


class TestCommandLineActorForActPhaseContentsOfExecutableFile(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        executable_file = sys.executable
        command_executor = CommandExecutorThatRecordsArguments()
        arrangement = Arrangement(
            source=remaining_source('= ' + actor_utils.COMMAND_LINE_ACTOR_NAME),
            act_phase_source_lines=[executable_file],
            os_services=os_services_access.new_for_cmd_exe(command_executor),
        )
        expected_command = asrt_command.matches_command(
            driver=asrt_command.matches_executable_file_command_driver(
                asrt_path.path_as_str(asrt.equals(executable_file)),
            ),
            arguments=asrt.is_empty_sequence
        )
        expectation = Expectation(
            symbol_usages=asrt.is_empty_sequence,
            after_execution=ExecutedCommandAssertion(command_executor,
                                                     lambda tcds: expected_command)
        )
        # ACT & ASSERT #
        check_actor_execution(self, arrangement, expectation)
