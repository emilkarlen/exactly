from typing import List

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity.actors import SOURCE_INTERPRETER_ACTOR
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.structures import section_contents
from exactly_lib.util.textformat.textformat_parser import TextParser


class InterpreterActorDocumentation(ActorDocumentation):
    def __init__(self):
        super().__init__(SOURCE_INTERPRETER_ACTOR)
        format_map = {
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'actor_option': formatting.cli_option(common_cli_options.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'shell_command': formatting.misc_name_with_formatting(misc_texts.SHELL_COMMAND),
        }
        self._parser = TextParser(format_map)

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._parser.fnap(_MAIN_DESCRIPTION_REST)

    def act_phase_contents(self) -> SectionContents:
        return section_contents(self._parser.fnap(_ACT_PHASE_CONTENTS))

    def act_phase_contents_syntax(self) -> SectionContents:
        return section_contents(self._parser.fnap(_ACT_PHASE_CONTENTS_SYNTAX))

    def _see_also_specific(self) -> List[SeeAlsoTarget]:
        return [
            syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT.cross_reference_target,
        ]


DOCUMENTATION = InterpreterActorDocumentation()

_MAIN_DESCRIPTION_REST = """\
The contents of the {phase[act]} phase is stored in a file, and the name of this file is given as
the last argument to the interpreter.
"""

_ACT_PHASE_CONTENTS = """\
Source code to be interpreted by the interpreter.
"""

_ACT_PHASE_CONTENTS_SYNTAX = """\
All lines of the {phase[act]} phase are part of the source code.

There is no recognition or special handling of comment lines and empty lines.
"""
