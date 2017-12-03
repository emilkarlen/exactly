from exactly_lib.help.contents_structure.entity import EntityTypeHelp, EntityDocumentation
from exactly_lib.help_texts.entity.all_entity_types import SUITE_REPORTER_ENTITY_TYPE_NAMES
from exactly_lib.help_texts.entity.concepts import SUITE_REPORTER_CONCEPT_INFO


class SuiteReporterDocumentation(EntityDocumentation):
    """
    Documents a suite reporter.
    """

    def main_description_rest(self) -> list:
        """
        :rtype [`ParagraphItem`]
        """
        return []

    def syntax_of_output(self) -> list:
        """
        :rtype [`ParagraphItem`]
        """
        return []

    def exit_code_description(self) -> list:
        """
        :rtype [`ParagraphItem`]
        """
        raise NotImplementedError()

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return self.__see_also_targets__common() + self._see_also_targets__specific()

    @staticmethod
    def __see_also_targets__common() -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return [
            SUITE_REPORTER_CONCEPT_INFO.cross_reference_target,
        ]

    def _see_also_targets__specific(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return []


def suite_reporters_help(suite_reporters: iter) -> EntityTypeHelp:
    """
    :param suite_reporters: [SuiteReporterDocumentation]
    """
    return EntityTypeHelp(SUITE_REPORTER_ENTITY_TYPE_NAMES,
                          suite_reporters)
