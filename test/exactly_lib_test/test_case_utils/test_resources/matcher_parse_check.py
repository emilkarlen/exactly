from typing import TypeVar

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

MODEL = TypeVar('MODEL')


class Expectation:
    def __init__(self,
                 sdv: ValueAssertion[SymbolDependentValue],
                 token_stream: ValueAssertion[TokenParser] = asrt.anything_goes()):
        self.sdv = sdv
        self.token_stream = token_stream
