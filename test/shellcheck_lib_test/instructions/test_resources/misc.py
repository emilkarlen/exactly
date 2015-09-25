import os
import unittest

from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions import utils


def single_line_source() -> utils.SingleInstructionParserSource:
    return utils.new_source('instruction name', 'instruction arguments')


class TestError(Exception):
    pass


class SvhRaisesTestError(svh_check.Assertion):
    def apply(self, put: unittest.TestCase, actual: svh.SuccessOrValidationErrorOrHardError):
        raise TestError()


class ShRaisesTestError(sh_check.Assertion):
    def apply(self, put: unittest.TestCase, actual: sh.SuccessOrHardError):
        raise TestError()


class PfhRaisesTestError(pfh_check.Assertion):
    def apply(self, put:
    unittest.TestCase,
              actual: pfh.PassOrFailOrHardError):
        raise TestError()


class EdsContentsRaisesTestError(eds_contents_check.Assertion):
    def apply(self, put: unittest.TestCase, eds: ExecutionDirectoryStructure):
        raise TestError()


class ParserThatGives(SingleInstructionParser):
    def __init__(self,
                 instruction: Instruction):
        self.instruction = instruction

    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> Instruction:
        return self.instruction


def raise_test_error_if_cwd_is_not_test_root(eds: ExecutionDirectoryStructure):
    cwd = os.getcwd()
    if cwd != str(eds.test_root_dir):
        raise TestError()
