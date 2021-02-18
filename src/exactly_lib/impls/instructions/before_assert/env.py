from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.before_assert.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase.environ import parse, doc


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(parse.parts_parser(phase_is_after_act=True)),
        doc.TheInstructionDocumentation(instruction_name))
