from exactly_lib.help.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help.entity_names import SUITE_REPORTER_ENTITY_TYPE_NAME
from exactly_lib.help.suite_reporters.names_and_cross_references import suite_reporter_cross_ref
from exactly_lib.help.utils.entity_documentation import EntityDocumentation, EntitiesHelp
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import Text


class SuiteReporterDocumentation(EntityDocumentation):
    """
    Abstract base class for concepts.
    """

    def __init__(self, name: str):
        self._name = name

    def singular_name(self) -> str:
        return self._name

    def cross_reference_target(self) -> EntityCrossReferenceId:
        return suite_reporter_cross_ref(self._name)

    def single_line_description(self) -> Text:
        return docs.text(self.single_line_description_str())

    def name_and_single_line_description(self) -> Text:
        return docs.text(self.name_and_single_line_description_str())

    def name_and_single_line_description_str(self) -> str:
        return self.singular_name() + ' - ' + self.single_line_description_str()

    def single_line_description_str(self) -> str:
        raise NotImplementedError()

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
        from exactly_lib.help.concepts.plain_concepts.suite_reporter import SUITE_REPORTER_CONCEPT
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
