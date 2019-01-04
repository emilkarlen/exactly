import unittest

import os

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser, \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.phases.common import TestCaseInstruction, InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.section_document.test_resources.parse_source import source_of_lines
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def single_line_source() -> ParseSource:
    return source_of_lines(['argument'])


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


class RaisesTestError(ValueAssertionBase):
    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        raise TestError()


def raises_test_error() -> ValueAssertion:
    return RaisesTestError()


class ParserThatGives(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self,
                 instruction: TestCaseInstruction):
        self.instruction = instruction

    def parse_from_source(self, source: ParseSource) -> TestCaseInstruction:
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