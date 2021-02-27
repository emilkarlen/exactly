import unittest
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Callable

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib_test.impls.types.parse.test_resources import \
    single_line_source_instruction_utils as equivalent_source_cases
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_resources.source import abs_stx_utils
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax

ARRANGEMENT = TypeVar('ARRANGEMENT')
EXPECTATION = TypeVar('EXPECTATION')


class InstructionChecker(Generic[ARRANGEMENT, EXPECTATION], ABC):
    def check_parsing__abs_stx(self,
                               put: unittest.TestCase,
                               parser: InstructionParser,
                               source: AbstractSyntax,
                               mk_arrangement: Callable[[], ARRANGEMENT],
                               expectation: EXPECTATION,
                               ):
        for formatting_case in abs_stx_utils.formatting_cases(source):
            for source_case in equivalent_source_cases.consume_last_line__s__nsc(formatting_case.value):
                with put.subTest(source_formatting=formatting_case,
                                 source_following=source_case.name):
                    source = source_case.source
                    instruction = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                    source_case.expectation.apply_with_message(put, source, 'source after parse')
                    self.check(put, instruction, mk_arrangement(), expectation)

    def check_parsing__abs_stx__const(self,
                                      put: unittest.TestCase,
                                      parser: InstructionParser,
                                      source: AbstractSyntax,
                                      arrangement: ARRANGEMENT,
                                      expectation: EXPECTATION,
                                      ):
        def mk_arrangement() -> ARRANGEMENT:
            return arrangement

        self.check_parsing__abs_stx(
            put,
            parser,
            source,
            mk_arrangement,
            expectation,
        )

    @abstractmethod
    def check(self,
              put: unittest.TestCase,
              instruction: Instruction,
              arrangement: ARRANGEMENT,
              expectation: EXPECTATION):
        """Checks all properties of the instruction"""
        pass
