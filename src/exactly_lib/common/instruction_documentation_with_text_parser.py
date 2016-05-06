from exactly_lib.common.instruction_documentation import InstructionDocumentation
from exactly_lib.help.utils.formatting import InstructionName
from exactly_lib.help.utils.textformat_parse import TextParser


class InstructionDocumentationWithTextParserBase(InstructionDocumentation):
    """
    A `InstructionDocumentation` with convenient access to a `TextParser`.

    The format_map of the `TextParser` always contains a key
    "instruction_name" which is the name of the instruction as a `InstructionName` object
    (which gives access to some formatting using the ":fmt" syntax).
    """

    def __init__(self,
                 instruction_name: str,
                 format_map: dict):
        super().__init__(instruction_name)
        fm = {'instruction_name': InstructionName(instruction_name)}
        fm.update(format_map)
        self._parser = TextParser(fm)

    def _format(self, s: str, extra: dict = None) -> str:
        return self._parser.format(s, extra)

    def _fnap(self, s: str, extra: dict = None) -> list:
        return self._parser.fnap(s, extra)
