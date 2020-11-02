from typing import Callable

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.multi_phase.define_symbol import doc, parser
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import InstructionPartsParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser


def setup(instruction_name: str,
          is_in_assert_phase: bool,
          mk_parser: Callable[[InstructionPartsParser], InstructionParser],
          ) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        mk_parser(parser.PARTS_PARSER),
        doc.TheInstructionDocumentation(instruction_name, is_in_assert_phase))
