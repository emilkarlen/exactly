from typing import Sequence

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class ParseExpectation:
    def __init__(
            self,
            source: Assertion[ParseSource] = asrt.anything_goes(),
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
    ):
        self.source = source
        self.symbol_usages = symbol_usages
