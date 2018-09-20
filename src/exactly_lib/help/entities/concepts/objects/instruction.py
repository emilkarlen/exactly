from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import suite_reporters as reporters, concepts
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.textformat_parser import TextParser


class _InstructionConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.INSTRUCTION_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'default_reporter': formatting.entity(reporters.DEFAULT_REPORTER.singular_name),
            'instruction_concept': formatting.concept(self.singular_name()),
            'instructions_concept_plain': self.name().plural,
            'act_phase': phase_infos.ACT.name,
        })
        return from_simple_description(
            Description(self.single_line_description(),
                        tp.fnap(_DESCRIPTION_REST)))


INSTRUCTION_CONCEPT = _InstructionConcept()

############################################################
# MENTION
#
# - Executable
# - Building block of all phases except [act]
# - Can succeed or cause in error - test case execution halts
#   when an instruction causes an error
# - Meaning of executing a phase (see description of test case:
#   ("executing a test case means executing all of its phases"
#    add - executing a phase means executing all of its instructions,
#    and halt at the first that causes an error)
#
# - Semantics:
#    - all phases except [assert]: is a side-effect
#    - [act]: some instructions are assertions
#      (more info in description of [act])
#
# - Syntax
#   - starts on new line
#   - have a name/identifier
#   - can span multiple lines
#   - syntax is defined by each instruction
############################################################
_DESCRIPTION_REST = """\
All phases except {act_phase:syntax} consts of a sequence of {instructions_concept_plain} -
zero or more.


Executing a phase means executing all {instructions_concept_plain} in the phase,
in the order they appear in the test case source file.
"""
