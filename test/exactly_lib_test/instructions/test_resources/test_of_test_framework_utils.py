import os
import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from exactly_lib.test_case.phases.common import HomeAndSds, TestCaseInstruction
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.test_resources import pfh_check
from exactly_lib_test.instructions.test_resources import sh_check
from exactly_lib_test.instructions.test_resources import svh_check
from exactly_lib_test.instructions.test_resources.assertion_utils.side_effects import SideEffectsCheck
from exactly_lib_test.test_resources.execution import eds_contents_check
from exactly_lib_test.test_resources.parse import new_source2


def single_line_source() -> SingleInstructionParserSource:
    return new_source2('argument')


class TestError(Exception):
    pass


class SvhRaisesTestError(svh_check.Assertion):
    def apply(self, put: unittest.TestCase, actual: svh.SuccessOrValidationErrorOrHardError):
        raise TestError()


class ShRaisesTestError(sh_check.Assertion):
    def apply(self, put: unittest.TestCase, actual: sh.SuccessOrHardError):
        raise TestError()


class PfhRaisesTestError(pfh_check.Assertion):
    def apply(self,
              put: unittest.TestCase,
              actual: pfh.PassOrFailOrHardError):
        raise TestError()


class EdsContentsRaisesTestError(eds_contents_check.Assertion):
    def apply(self, put: unittest.TestCase, eds: SandboxDirectoryStructure):
        raise TestError()


class SideEffectsCheckThatRaisesTestError(SideEffectsCheck):
    def apply(self,
              put: unittest.TestCase,
              home_and_sds: HomeAndSds):
        raise TestError()


class ParserThatGives(SingleInstructionParser):
    def __init__(self,
                 instruction: TestCaseInstruction):
        self.instruction = instruction

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        return self.instruction


def raise_test_error_if_cwd_is_not_test_root(eds: SandboxDirectoryStructure):
    cwd = os.getcwd()
    if cwd != str(eds.act_dir):
        raise TestError()
