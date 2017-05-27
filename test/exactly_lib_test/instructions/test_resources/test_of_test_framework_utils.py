import os
import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.phases.common import TestCaseInstruction, InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.parse import source3
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def single_line_source() -> ParseSource:
    return source3(['argument'])


class TestError(Exception):
    pass


class TestCaseWithTestErrorAsFailureException(unittest.TestCase):
    def __init__(self):
        super().__init__()
        self.failureException = TestError


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.tc = TestCaseWithTestErrorAsFailureException()

    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement,
               expectation):
        raise NotImplementedError()


class RaisesTestError(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        raise TestError()


def raises_test_error() -> va.ValueAssertion:
    return RaisesTestError()


class ParserThatGives(InstructionParser):
    def __init__(self,
                 instruction: TestCaseInstruction):
        self.instruction = instruction

    def parse(self, source: ParseSource) -> TestCaseInstruction:
        return self.instruction


def raise_test_error_if_cwd_is_not_test_root(sds: SandboxDirectoryStructure):
    cwd = os.getcwd()
    if cwd != str(sds.act_dir):
        raise TestError()


def raise_test_error_if_cwd_is_not_act_root__env(environment: InstructionEnvironmentForPostSdsStep,
                                                 *args,
                                                 **kwargs):
    cwd = os.getcwd()
    if cwd != str(environment.sds.act_dir):
        raise TestError()
