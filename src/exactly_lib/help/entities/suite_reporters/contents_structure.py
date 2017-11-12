from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase, EntityTypeNames
from exactly_lib.help_texts.entity.concepts import SUITE_REPORTER_CONCEPT_INFO
from exactly_lib.help_texts.names import formatting

SUITE_REPORTER_ENTITY_TYPE_NAMES = EntityTypeNames(SUITE_REPORTER_CONCEPT_INFO.name,
                                                   'reporter',
                                                   formatting.syntax_element(SUITE_REPORTER_CONCEPT_INFO.singular_name))


class SuiteReporterDocumentation(EntityDocumentationBase):
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
        from exactly_lib.help.entities.concepts.plain_concepts.suite_reporter import SUITE_REPORTER_CONCEPT
        return [
            SUITE_REPORTER_CONCEPT.cross_reference_target(),
        ]

    def _see_also_targets__specific(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return []


def suite_reporters_help(suite_reporters: iter) -> EntitiesHelp:
    """
    :param suite_reporters: [SuiteReporterDocumentation]
    """
    return EntitiesHelp(SUITE_REPORTER_ENTITY_TYPE_NAMES,
                        suite_reporters)
