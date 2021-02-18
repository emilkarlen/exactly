from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.multi_phase.environ import parse, doc
from exactly_lib.impls.instructions.setup.utils import instruction_from_parts


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(parse.parts_parser(phase_is_after_act=False)),
        doc.TheInstructionDocumentation(instruction_name,
                                        is_in_setup_phase=True))
