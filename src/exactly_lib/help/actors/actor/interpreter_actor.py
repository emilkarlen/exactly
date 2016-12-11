from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options
from exactly_lib.default.program_modes.test_case.default_instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help.actors.contents_structure import ActorDocumentation
from exactly_lib.help.actors.names_and_cross_references import INTERPRETER_ACTOR
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.cross_reference_id import TestCasePhaseInstructionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils import suite_section_names
from exactly_lib.help.utils.phase_names import phase_name_dictionary, CONFIGURATION_PHASE_NAME
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.test_case import sandbox_directory_structure as sds
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.structures import section_contents


class InterpreterActorDocumentation(ActorDocumentation):
    def __init__(self):
        super().__init__(INTERPRETER_ACTOR)
        from exactly_lib.execution.exit_values import EXECUTION__VALIDATE
        format_map = {
            'phase': phase_name_dictionary(),
            'home_directory': HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular,
            'sandbox': SANDBOX_CONCEPT.name().singular,
            'result_subdir': sds.SUB_DIRECTORY__RESULT,
            'VALIDATION': EXECUTION__VALIDATE.exit_identifier,
            'actor_option': formatting.cli_option(command_line_options.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
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
            TestSuiteSectionInstructionCrossReference(suite_section_names.CONFIGURATION_SECTION_NAME.plain,
                                                      ACTOR_INSTRUCTION_NAME),
        ]


DOCUMENTATION = InterpreterActorDocumentation()

_MAIN_DESCRIPTION_REST = """\
The contents of the {phase[act]} phase is stored in a file, and the name of this file is given as
the last argument to the given interpreter.

If the interpreter is a shell command, then the quoted file name (according to shell syntax) is appended
to the end of the command string.


The interpreter may be specified, either via the {actor_instruction} instruction
(both in test cases and test suites),
or the {actor_option} command line option.
"""

_ACT_PHASE_CONTENTS = """\
Source code to be interpreted by the given interpreter.
"""

_ACT_PHASE_CONTENTS_SYNTAX = """\
All lines of the {phase[act]} phase are part of the source code.

There is no recognition or special handling of comment lines and empty lines.
"""
