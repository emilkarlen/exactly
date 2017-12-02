from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.formatting import InstructionName
from exactly_lib.help_texts.test_case.phase_names import ASSERT_PHASE_NAME
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose, AssertPhasePurpose
from exactly_lib.util.cli_syntax.render import cli_program_syntax
from exactly_lib.util.textformat.structure.core import Text
from exactly_lib.util.textformat.textformat_parser import TextParser


class InstructionDocumentationWithTextParserBase(InstructionDocumentation):
    """
    A `InstructionDocumentation` with convenient access to a `TextParser`.

    The format_map of the `TextParser` always contains a key
    "instruction_name" which is the name of the instruction as a `InstructionName` object
    (which gives access to some rendering using the ":fmt" syntax).
    """

    def __init__(self,
                 instruction_name: str,
                 format_map: dict):
        super().__init__(instruction_name)
        fm = {'instruction_name': InstructionName(instruction_name)}
        fm.update(format_map)
        self._tp = TextParser(fm)

    def _format(self, s: str, extra: dict = None) -> str:
        return self._tp.format(s, extra)

    def _text(self, s: str, extra: dict = None) -> Text:
        return self._tp.text(s, extra)

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._tp.fnap(s, extra)


class InstructionDocumentationWithCommandLineRenderingBase(InstructionDocumentationWithTextParserBase):
    """
    Base class for instruction documentations that supplies utility methods for
    command lines made up of a `CommandLine`.
    """

    CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

    def __init__(self,
                 instruction_name: str,
                 format_map: dict):
        super().__init__(instruction_name, format_map)

    def _cl_syntax_for_args(self, argument_usages: list) -> str:
        return cl_syntax.cl_syntax_for_args(argument_usages)


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
    InstructionDocumentationWithCommandLineRenderingAndSplittedPartsForRestDocBase,
    WithAssertPhasePurpose):
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

    @property
    def assert_phase_purpose(self) -> AssertPhasePurpose:
        return AssertPhasePurpose.HELPER

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
