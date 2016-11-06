from exactly_lib.common.instruction_documentation import InvokationVariant, SyntaxElementDescription
from exactly_lib.instructions.utils.cmd_and_args_resolvers import ConstantCmdAndArgsResolver
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingAndSplittedPartsForRestDocBase
from exactly_lib.instructions.utils.instruction_from_parts_for_executing_sub_process import \
    MainStepExecutorForSubProcess, ValidationAndSubProcessExecutionSetup
from exactly_lib.instructions.utils.instruction_parts import InstructionParts
from exactly_lib.instructions.utils.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.instructions.utils.sub_process_execution import InstructionSourceInfo
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.util.cli_syntax.elements import argument as a

_COMMAND_SYNTAX_ELEMENT = 'COMMAND'


class TheInstructionDocumentationBase(InstructionDocumentationWithCommandLineRenderingAndSplittedPartsForRestDocBase):
    def __init__(self, name: str):
        super().__init__(name, {'COMMAND': _COMMAND_SYNTAX_ELEMENT})
        self.command_arg = a.Named(_COMMAND_SYNTAX_ELEMENT)

    def single_line_description(self) -> str:
        return "Executes a command using the current system's shell"

    def _main_description_rest_body(self) -> list:
        text = """\
        Which commands are available and the syntax of them depends
        on the current system's shell and environment.


        The shell takes care of interpreting {COMMAND}, so all features of the
        shell can be used.


        Use of the {instruction_name} instruction is not portable since it
        uses the current operating system environment's shell.


        On POSIX, the shell defaults to /bin/sh.

        On Windows, the COMSPEC environment variable specifies the default shell.
        """
        return self._paragraphs(text)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         self.command_arg)]),
                []),
        ]

    def syntax_element_descriptions(self) -> list:
        text = """\
        Something that is understood by the current system's shell.
        """
        return [
            SyntaxElementDescription(self.command_arg.name,
                                     self._paragraphs(text))
        ]


class DescriptionForNonAssertPhaseInstruction(TheInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name)

    def _main_description_rest_prelude(self) -> list:
        text = """\
        It is considered an error if {COMMAND} exits with a non-zero exit code.
        """
        return self._paragraphs(text)


class Parser(SingleInstructionParser):
    def __init__(self,
                 instruction_name: str,
                 instruction_setup_2_instruction_function):
        self.instruction_name = instruction_name
        self.instruction_setup_2_instruction_function = instruction_setup_2_instruction_function

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        argument = source.instruction_argument.strip()
        if not argument:
            msg = _COMMAND_SYNTAX_ELEMENT + ' must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)
        setup = ValidationAndSubProcessExecutionSetup(
            InstructionSourceInfo(source.line_sequence.first_line.line_number,
                                  self.instruction_name),
            ConstantSuccessValidator(),
            ConstantCmdAndArgsResolver(argument),
            is_shell=True)
        instruction_setup = InstructionParts(setup.validator,
                                             MainStepExecutorForSubProcess(setup))
        return self.instruction_setup_2_instruction_function(instruction_setup)
