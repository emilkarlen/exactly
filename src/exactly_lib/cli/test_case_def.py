from typing import List

from exactly_lib.cli.builtin_symbol import BuiltinSymbol
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup


class TestCaseDefinitionForMainProgram:
    """
    Corresponds to TestCaseDefinition, but with
    extra information about predefined symbols for the help system.
    """

    def __init__(self,
                 test_case_parsing_setup: TestCaseParsingSetup,
                 builtin_symbols: List[BuiltinSymbol],
                 ):
        self.test_case_parsing_setup = test_case_parsing_setup
        self.builtin_symbols = builtin_symbols
