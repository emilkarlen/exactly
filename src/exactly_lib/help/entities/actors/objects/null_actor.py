from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.help_texts.entity import actors
from exactly_lib.help_texts.entity.concepts import ACTOR_CONCEPT_INFO
from exactly_lib.help_texts.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME
from exactly_lib.help_texts.test_suite import formatted_section_names
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.structures import section_contents
from exactly_lib.util.textformat.textformat_parser import TextParser


class NullActorDocumentation(ActorDocumentation):
    def __init__(self):
        super().__init__(actors.NULL_ACTOR)
        format_map = {
            'null': actors.NULL_ACTOR.singular_name,
            'actor': ACTOR_CONCEPT_INFO.name.singular,
        }
        self._parser = TextParser(format_map)

    def main_description_rest(self) -> list:
        return self._parser.fnap(_MAIN_DESCRIPTION_REST)

    def act_phase_contents(self) -> SectionContents:
        return section_contents(self._parser.fnap(_ACT_PHASE_CONTENTS))

    def act_phase_contents_syntax(self) -> SectionContents:
        return section_contents(self._parser.fnap(_ACT_PHASE_CONTENTS_SYNTAX))

    def _see_also_specific(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   ACTOR_INSTRUCTION_NAME),
            TestSuiteSectionInstructionCrossReference(formatted_section_names.CONFIGURATION_SECTION_NAME.plain,
                                                      ACTOR_INSTRUCTION_NAME),
        ]


DOCUMENTATION = NullActorDocumentation()

_ACT_PHASE_CONTENTS = """\
Ignored.
"""

_ACT_PHASE_CONTENTS_SYNTAX = """\
There are no syntax requirements.
"""

_MAIN_DESCRIPTION_REST = """\
The {null} {actor} is useful when the test case does not test a program,
but rather properties of the operating system environment.
"""
