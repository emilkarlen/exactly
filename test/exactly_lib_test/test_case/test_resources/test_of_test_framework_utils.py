import os
import unittest

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser, \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib_test.section_document.test_resources.parse_source import source_of_lines
from exactly_lib_test.test_resources.arguments.arguments_building import Arguments
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase


def single_line_source() -> ParseSource:
    return source_of_lines(['argument'])


def single_line_arguments() -> Arguments:
    return Arguments('argument')


def empty_arguments() -> Arguments:
    return Arguments('')


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


class RaisesTestError(AssertionBase):
    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        raise TestError()


def raises_test_error() -> Assertion:
    return RaisesTestError()


class ParserThatGives(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self,
                 instruction: TestCaseInstruction):
        self.instruction = instruction

    def parse_from_source(self, source: ParseSource) -> TestCaseInstruction:
        return self.instruction


def raise_test_error_if_cwd_is_not_test_root(sds: SandboxDs):
    cwd = os.getcwd()
    if cwd != str(sds.act_dir):
        raise TestError()


def raise_test_error_if_cwd_is_not_act_root__env(environment: InstructionEnvironmentForPostSdsStep,
                                                 *args):
    cwd = os.getcwd()
    if cwd != str(environment.sds.act_dir):
        raise TestError()
