from typing import List, Dict, Any

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose, AssertPhasePurpose
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents
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
                 format_map: Dict[str, Any],
                 ):
        super().__init__(instruction_name)
        self._tp = TextParser(format_map)


class InstructionDocumentationWithSplittedPartsForRestDocBase(InstructionDocumentationWithTextParserBase):
    """
    Base class for instruction documentations that has splits the "rest" part of the documentation into

    1. prologue
    2. body
    3. epilogue

    Sub classes must implement at least `_main_description_rest_body`.

    Sub classes must _not_ override `main_description_rest`.
    """

    def main_description_rest(self) -> List[ParagraphItem]:
        return (self._main_description_rest_prologue() +
                self._main_description_rest_body() +
                self._main_description_rest_epilogue())

    def _main_description_rest_prologue(self) -> List[ParagraphItem]:
        return []

    def _main_description_rest_body(self) -> List[ParagraphItem]:
        return []

    def _main_description_rest_epilogue(self) -> List[ParagraphItem]:
        return []


class InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase(
    InstructionDocumentationWithSplittedPartsForRestDocBase,
    WithAssertPhasePurpose):
    def __init__(self,
                 instruction_name: str,
                 format_map: Dict[str, str],
                 is_in_assert_phase: bool):
        the_format_map = {
            'assert_phase': phase_names.ASSERT,
        }
        if format_map:
            the_format_map.update(format_map)
        super().__init__(instruction_name, the_format_map)
        self._is_in_assert_phase = is_in_assert_phase

    @property
    def assert_phase_purpose(self) -> AssertPhasePurpose:
        return AssertPhasePurpose.HELPER

    def notes(self) -> SectionContents:
        paragraphs = self._notes__specific()

        if self._is_in_assert_phase:
            paragraphs += self._tp.fnap(_NOT_AN_ASSERTION_IN_ASSERT_PHASE)

        return SectionContents(paragraphs)

    def _notes__specific(self) -> List[ParagraphItem]:
        return []

    def _main_description_rest_prologue(self) -> List[ParagraphItem]:
        return []


_NOT_AN_ASSERTION_IN_ASSERT_PHASE = """\
In the {assert_phase} phase, this instruction is mostly useful as a helper for writing
assertions.
The instruction is not an assertion on its own.
"""
