from typing import Tuple, Callable, List, Dict

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo


class SingleInstructionSetup(InstructionParser):
    def __init__(self,
                 parser: InstructionParser,
                 documentation: InstructionDocumentation):
        self._parser = parser
        self._documentation = documentation

    @property
    def documentation(self) -> InstructionDocumentation:
        return self._documentation

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> Instruction:
        return self._parser.parse(fs_location_info, source)


def instruction_set_from_name_and_setup_constructor_list(
        name_and_setup_constructor_list: List[Tuple[str, Callable[[str], SingleInstructionSetup]]]
) -> Dict[str, SingleInstructionSetup]:
    return {
        name: setup_constructor(name)
        for name, setup_constructor in name_and_setup_constructor_list
    }
