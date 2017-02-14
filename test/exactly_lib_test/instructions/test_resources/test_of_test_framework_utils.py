import os
import unittest

from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionParserSource
from exactly_lib.section_document.parser_implementations.new_section_element_parser import InstructionParser
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.parse import new_source2, source3
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def single_line_source() -> SingleInstructionParserSource:
    return new_source2('argument')


# TODO [instr-desc] Remove other with new parsing integrated
def single_line_sourceInstrDesc() -> ParseSource:
    return source3(['argument'])


class TestError(Exception):
    pass


class RaisesTestError(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        raise TestError()


def raises_test_error() -> va.ValueAssertion:
    return RaisesTestError()


class ParserThatGives(SingleInstructionParser):
    def __init__(self,
                 instruction: TestCaseInstruction):
        self.instruction = instruction

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        return self.instruction


# TODO [instr-desc] Remove other with new parsing integrated
class ParserThatGivesInstrDesc(InstructionParser):
    def __init__(self,
                 instruction: TestCaseInstruction):
        self.instruction = instruction

    def parse(self, source: ParseSource) -> TestCaseInstruction:
        return self.instruction


def raise_test_error_if_cwd_is_not_test_root(sds: SandboxDirectoryStructure):
    cwd = os.getcwd()
    if cwd != str(sds.act_dir):
        raise TestError()
