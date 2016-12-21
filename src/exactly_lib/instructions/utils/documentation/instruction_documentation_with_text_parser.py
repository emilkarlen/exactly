from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help.utils.formatting import InstructionName
from exactly_lib.help.utils.phase_names import ASSERT_PHASE_NAME
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.instructions.utils.documentation.documentation_text import CommandLineRenderingHelper
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax
from exactly_lib.util.textformat.structure.core import Text


class InstructionDocumentationWithTextParserBase(InstructionDocumentation):
    """
    A `InstructionDocumentation` with convenient access to a `TextParser`.

    The format_map of the `TextParser` always contains a key
    "instruction_name" which is the name of the instruction as a `InstructionName` object
    (which gives access to some formatting using the ":fmt" syntax).
    """

    def __init__(self,
                 instruction_name: str,
                 format_map: dict):
        super().__init__(instruction_name)
        fm = {'instruction_name': InstructionName(instruction_name)}
        fm.update(format_map)
        self._parser = TextParser(fm)

    def _format(self, s: str, extra: dict = None) -> str:
        return self._parser.format(s, extra)

    def _text(self, s: str, extra: dict = None) -> Text:
        return self._parser.text(s, extra)

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)


class InstructionDocumentationWithCommandLineRenderingBase(InstructionDocumentationWithTextParserBase):
    """
    Base class for instruction documentations that supplies utility methods for
    command lines made up of a `CommandLine`.
    """

    CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

    ARG_SYNTAX_RENDERER = cli_program_syntax.ArgumentInArgumentDescriptionRenderer()

    def __init__(self,
                 instruction_name: str,
                 format_map: dict):
        super().__init__(instruction_name, format_map)
        self.clr = CommandLineRenderingHelper()

    def _cl_syntax_for_args(self, argument_usages: list) -> str:
        return self.clr.cl_syntax_for_args(argument_usages)

    def _cl_syntax(self, command_line: a.CommandLine) -> str:
        return self.clr.cl_syntax(command_line)

    def _arg_syntax(self, arg: a.Argument) -> str:
        return self.clr.arg_syntax(arg)

    def _cli_argument_syntax_element_description(self,
                                                 argument: a.Argument,
                                                 description_rest: list) -> SyntaxElementDescription:
        return self.clr.cli_argument_syntax_element_description(argument, description_rest)


class InstructionDocumentationWithCommandLineRenderingAndSplittedPartsForRestDocBase(
    InstructionDocumentationWithCommandLineRenderingBase):
    """
    Base class for instruction documentations that has splits the "rest" part of the documentation into

    1. prelude
    2. body
    3. prologue

    Sub classes must implement at least `_main_description_rest_body`.

    Sub classes must _not_ override `main_description_rest`.
    """

    def main_description_rest(self) -> list:
        return (self._main_description_rest_prelude() +
                self._main_description_rest_body() +
                self._main_description_rest_prologue())

    def _main_description_rest_prelude(self) -> list:
        return []

    def _main_description_rest_body(self) -> list:
        raise NotImplementedError()

    def _main_description_rest_prologue(self) -> list:
        return []


class InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase(
    InstructionDocumentationWithCommandLineRenderingAndSplittedPartsForRestDocBase):
    def __init__(self, instruction_name: str,
                 format_map: dict,
                 is_in_assert_phase: bool):
        the_format_map = {
            'assert_phase': ASSERT_PHASE_NAME,
        }
        if format_map:
            the_format_map.update(format_map)
        super().__init__(instruction_name, the_format_map)
        self._is_in_assert_phase = is_in_assert_phase

    def _main_description_rest_prelude(self) -> list:
        if self._is_in_assert_phase:
            return self._paragraphs(_NOT_AN_ASSERTION_IN_ASSERT_PHASE)
        else:
            return []


_NOT_AN_ASSERTION_IN_ASSERT_PHASE = """\
Note:
In the {assert_phase} phase, this instruction is mostly useful as a helper for writing
assertions.  The instruction is not an assertion on its own.
"""
