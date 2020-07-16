from typing import Sequence

from exactly_lib.section_document.model import Instruction
from exactly_lib.symbol.sdv_structure import SymbolUsage


class TestCaseInstruction(Instruction):
    pass


class SymbolUser:
    """
    An object that may use symbols.
    
    Such an object must be able to tell which symbols are used and how they are used.
    """

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        """
        Gives information about all symbols that this instruction uses.

        This list should be available right after construction (and thus should not need
        any phase step to have been executed). The return value must be constant, with regard
        to the execution of other methods on the object (object of a sub class of this class).

        A symbol definition should not report references that the definition uses -
        these references are derived automatically via the definition object.

        :return: [`SymbolUsage`]
        """
        return []


class TestCaseInstructionWithSymbols(TestCaseInstruction, SymbolUser):
    pass
