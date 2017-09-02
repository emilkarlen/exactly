from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.utils.entity_documentation import EntitiesHelp


class EntityConfiguration(tuple):
    def __new__(cls,
                entities_help: EntitiesHelp,
                entity_doc_2_section_contents_renderer,
                entities_doc_2_section_contents_renderer):
        return tuple.__new__(cls, (entities_help,
                                   entity_doc_2_section_contents_renderer,
                                   entities_doc_2_section_contents_renderer))

    @property
    def entities_help(self) -> EntitiesHelp:
        return self[0]

    @property
    def entity_doc_2_section_contents_renderer(self):
        """
        :rtype: `EntityDocumentation` -> `SectionContentsRenderer`
        """
        return self[1]

    @property
    def entities_doc_2_section_contents_renderer(self):
        """
        :rtype: iterable -> `SectionContentsRenderer`
        """
        return self[2]


class ApplicationHelp(tuple):
    def __new__(cls,
                main_program_help: MainProgramHelp,
                test_case_help: TestCaseHelp,
                test_suite_help: TestSuiteHelp,
                entity_name_2_entity_configuration: dict = ()):
        """
        :type entity_helps: list of `EntitiesHelp`
        :param entity_name_2_entity_configuration:
        """
        return tuple.__new__(cls, (main_program_help,
                                   test_case_help,
                                   test_suite_help,
                                   dict(entity_name_2_entity_configuration)),
                             )

    @property
    def main_program_help(self) -> MainProgramHelp:
        return self[0]

    @property
    def test_case_help(self) -> TestCaseHelp:
        return self[1]

    @property
    def test_suite_help(self) -> TestSuiteHelp:
        return self[2]

    @property
    def entity_name_2_entity_configuration(self) -> dict:
        """
        entity-name -> EntityConfiguration

        :return: str -> :class:`EntityConfiguration`
        """
        return self[3]
