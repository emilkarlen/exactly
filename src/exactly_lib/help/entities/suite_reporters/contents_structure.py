from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem
from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase
from exactly_lib.help_texts.entity_names import SUITE_REPORTER_ENTITY_TYPE_NAME


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

    def see_also_items(self) -> list:
        """
        :rtype: [`SeeAlsoItem`]
        """
        return [CrossReferenceIdSeeAlsoItem(x) for x in self.see_also()]

    def see_also(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        return self.__see_also_common() + self._see_also_specific()

    @staticmethod
    def __see_also_common() -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        from exactly_lib.help.entities.concepts.plain_concepts.suite_reporter import SUITE_REPORTER_CONCEPT
        return [
            SUITE_REPORTER_CONCEPT.cross_reference_target(),
        ]

    def _see_also_specific(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        return []


def suite_reporters_help(suite_reporters: iter) -> EntitiesHelp:
    """
    :param suite_reporters: [SuiteReporterDocumentation]
    """
    return EntitiesHelp(SUITE_REPORTER_ENTITY_TYPE_NAME, suite_reporters)
