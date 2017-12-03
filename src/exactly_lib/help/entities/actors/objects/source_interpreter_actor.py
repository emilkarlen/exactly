from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options
from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.help_texts.entity import concepts, conf_params
from exactly_lib.help_texts.entity.actors import SOURCE_INTERPRETER_ACTOR
from exactly_lib.help_texts.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME, \
    PHASE_NAME_DICTIONARY
from exactly_lib.help_texts.test_suite import formatted_section_names
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.structures import section_contents
from exactly_lib.util.textformat.textformat_parser import TextParser


class InterpreterActorDocumentation(ActorDocumentation):
    def __init__(self):
        super().__init__(SOURCE_INTERPRETER_ACTOR)
        from exactly_lib.processing.exit_values import EXECUTION__VALIDATE
        format_map = {
            'phase': PHASE_NAME_DICTIONARY,
            'home_directory': formatting.conf_param_(conf_params.HOME_CASE_DIRECTORY_CONF_PARAM_INFO),
            'sandbox': formatting.concept_(concepts.SANDBOX_CONCEPT_INFO),
            'result_subdir': sds.SUB_DIRECTORY__RESULT,
            'VALIDATION': EXECUTION__VALIDATE.exit_identifier,
            'actor_option': formatting.cli_option(command_line_options.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
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
            concepts.SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target,
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   ACTOR_INSTRUCTION_NAME),
            TestSuiteSectionInstructionCrossReference(formatted_section_names.CONFIGURATION_SECTION_NAME.plain,
                                                      ACTOR_INSTRUCTION_NAME),
        ]


DOCUMENTATION = InterpreterActorDocumentation()

_MAIN_DESCRIPTION_REST = """\
The contents of the {phase[act]} phase is stored in a file, and the name of this file is given as
the last argument to the given interpreter.

If the interpreter is a shell command, then the quoted file name (according to {shell_syntax_concept}) is appended
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
