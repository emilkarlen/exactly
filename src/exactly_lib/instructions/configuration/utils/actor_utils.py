import shlex

from exactly_lib.act_phase_setups import shell_command
from exactly_lib.act_phase_setups.source_interpreter.interpreter_setup import new_for_script_language_handling
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import SourceInterpreterSetup
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import StandardSourceFileManager
from exactly_lib.common.instruction_documentation import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.phase_names import ACT_PHASE_NAME
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.util.cli_syntax.elements import argument as a

SHELL_COMMAND_ACTOR_KEYWORD = 'shell'

INTERPRETER_ACTOR_KEYWORD = 'interpreter'


class InstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str,
                 single_line_description_unformatted: str,
                 main_description_rest_unformatted: str = None):
        self.executable = a.Named('EXECUTABLE')
        self.argument = a.Named('ARGUMENT')
        self.single_line_description_unformatted = single_line_description_unformatted
        self.main_description_rest_unformatted = main_description_rest_unformatted
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        super().__init__(name, {
            'EXECUTABLE': self.executable.name,
            'ARGUMENT': self.argument.name,
            'actor': formatting.concept(ACTOR_CONCEPT.name().singular),
            'act_phase': ACT_PHASE_NAME.emphasis,
        })

    def single_line_description(self) -> str:
        return self._format(self.single_line_description_unformatted)

    def invokation_variants(self) -> list:
        shell_arg = a.Single(a.Multiplicity.MANDATORY, a.Named(SHELL_COMMAND_ACTOR_KEYWORD))
        interpreter_arg = a.Single(a.Multiplicity.OPTIONAL, a.Named(INTERPRETER_ACTOR_KEYWORD))
        executable_arg = a.Single(a.Multiplicity.MANDATORY, self.executable)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE, self.argument)
        return [
            InvokationVariant(self._cl_syntax_for_args([shell_arg]),
                              self._description_of_shell()),
            InvokationVariant(self._cl_syntax_for_args([interpreter_arg,
                                                        executable_arg,
                                                        optional_arguments_arg]),
                              self._description_of_interpreter()),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self.executable.name,
                                     self._paragraphs(_DESCRIPTION_OF_EXECUTABLE)),
            SyntaxElementDescription(self.argument.name,
                                     self._paragraphs(_DESCRIPTION_OF_ARGUMENTS))
        ]

    def main_description_rest(self) -> list:
        if self.main_description_rest_unformatted:
            return self._paragraphs(self.main_description_rest_unformatted)
        else:
            return []

    def see_also(self) -> list:
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        return [
            ACTOR_CONCEPT.cross_reference_target(),
        ]

    def _description_of_interpreter(self) -> list:
        return self._paragraphs(_DESCRIPTION_OF_INTERPRETER)

    def _description_of_shell(self) -> list:
        return self._paragraphs(_DESCRIPTION_OF_SHELL)


def parse(source: SingleInstructionParserSource) -> ActPhaseHandling:
    """
    :raises SingleInstructionInvalidArgumentException In case of invalid syntax
    """
    arg = source.instruction_argument.strip()
    if arg == '':
        raise SingleInstructionInvalidArgumentException('An actor must be given.')
    if arg == SHELL_COMMAND_ACTOR_KEYWORD:
        return shell_command.act_phase_setup()
    args = arg.split(maxsplit=1)
    if args:
        if args[0] == SHELL_COMMAND_ACTOR_KEYWORD and len(args) > 1:
            raise SingleInstructionInvalidArgumentException('Superfluous argument to ' + SHELL_COMMAND_ACTOR_KEYWORD)
    try:
        command_and_arguments = shlex.split(arg)
    except:
        raise SingleInstructionInvalidArgumentException('Invalid quoting: ' + arg)
    if len(command_and_arguments) > 0 and command_and_arguments[0] == INTERPRETER_ACTOR_KEYWORD:
        del command_and_arguments[0]
    if not command_and_arguments:
        raise SingleInstructionInvalidArgumentException('Missing interpreter')

    act_phase_setup = new_for_script_language_handling(
        SourceInterpreterSetup(StandardSourceFileManager(
            'src',
            command_and_arguments[0],
            command_and_arguments[1:])))
    return act_phase_setup


_DESCRIPTION_OF_INTERPRETER = """\
The {act_phase} phase is source code, to be interpreted by the given {EXECUTABLE}.


{EXECUTABLE} is an executable program which is given {ARGUMENT}, followed by the name of a file
containing the contents of the {act_phase} phase, as arguments.
"""

_DESCRIPTION_OF_SHELL = """\
The {act_phase} phase is a single command line, which is execute it via the
systems' shell.
"""

_DESCRIPTION_OF_EXECUTABLE = """\
The path of an existing executable file.


Uses shell syntax.
"""

_DESCRIPTION_OF_ARGUMENTS = """\
Arguments given to {EXECUTABLE}.


Uses shell syntax.
"""
