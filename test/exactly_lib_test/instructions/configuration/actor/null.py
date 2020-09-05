import unittest

from exactly_lib.instructions.configuration import actor as sut
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol import symbol_syntax
from exactly_lib.test_case_utils.os_services import os_services_access
from exactly_lib_test.instructions.configuration.actor.test_resources import Arrangement, Expectation, \
    check_actor_execution
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatRecordsArguments
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestNullActor)


class TestNullActor(unittest.TestCase):
    def test_successful_setting(self):
        # ARRANGE #
        command_executor = CommandExecutorThatRecordsArguments()
        arrangement = Arrangement(
            source=remaining_source('= ' + actor_utils.NULL_ACTOR_NAME),
            act_phase_source_lines=['should',
                                    'be',
                                    'ignored',
                                    symbol_syntax.symbol_reference_syntax_for_name('symbol'),
                                    ],
            os_services=os_services_access.new_for_cmd_exe(command_executor),
        )
        expectation = Expectation(
            symbol_usages=asrt.is_empty_sequence,
            sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                exit_code=asrt.equals(0),
                stdout=asrt.equals(''),
                stderr=asrt.equals(''),
            )
        )
        # ACT & ASSERT #
        check_actor_execution(self, arrangement, expectation)

    def test_superfluous_arguments(self):
        source = remaining_source('= {} superfluous'.format(actor_utils.NULL_ACTOR_NAME))
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().parse(ARBITRARY_FS_LOCATION_INFO, source)
