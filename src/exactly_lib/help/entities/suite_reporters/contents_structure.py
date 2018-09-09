from typing import List, Iterable

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity.all_entity_types import SUITE_REPORTER_ENTITY_TYPE_NAMES
from exactly_lib.definitions.entity.concepts import SUITE_REPORTER_CONCEPT_INFO
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, EntityDocumentation
from exactly_lib.util.textformat.structure.core import ParagraphItem


class SuiteReporterDocumentation(EntityDocumentation):
    """
    Documents a suite reporter.
    """

    def main_description_rest(self) -> List[ParagraphItem]:
        return []

    def syntax_of_output(self) -> List[ParagraphItem]:
        return []

    def exit_code_description(self) -> List[ParagraphItem]:
        raise NotImplementedError()

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list which may contain duplicate elements.
        """
        return self.__see_also_targets__common() + self._see_also_targets__specific()

    @staticmethod
    def __see_also_targets__common() -> List[SeeAlsoTarget]:
        """
        :returns: A new list which may contain duplicate elements.
        """
        return [
            SUITE_REPORTER_CONCEPT_INFO.cross_reference_target,
        ]

    def _see_also_targets__specific(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list which may contain duplicate elements.
        """
        return []


def suite_reporters_help(suite_reporters: Iterable[SuiteReporterDocumentation]) -> EntityTypeHelp:
    return EntityTypeHelp(SUITE_REPORTER_ENTITY_TYPE_NAMES,
                          suite_reporters)
