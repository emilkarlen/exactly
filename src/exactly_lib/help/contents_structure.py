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
                concepts_help: EntitiesHelp,
                actors_help: EntitiesHelp,
                test_case_help: TestCaseHelp,
                test_suite_help: TestSuiteHelp,
                suite_reporters_help: EntitiesHelp,
                types_help: EntitiesHelp,
                entity_name_2_entity_configuration: dict = ()):
        return tuple.__new__(cls, (main_program_help,
                                   concepts_help,
                                   test_case_help,
                                   test_suite_help,
                                   actors_help,
                                   suite_reporters_help,
                                   types_help,
                                   dict(map(lambda eh: (eh.entity_type_name, eh),
                                            [concepts_help,
                                             actors_help,
                                             suite_reporters_help,
                                             types_help])),
                                   dict(entity_name_2_entity_configuration)),
                             )

    @property
    def main_program_help(self) -> MainProgramHelp:
        return self[0]

    @property
    def concepts_help(self) -> EntitiesHelp:
        return self[1]

    @property
    def test_case_help(self) -> TestCaseHelp:
        return self[2]

    @property
    def test_suite_help(self) -> TestSuiteHelp:
        return self[3]

    @property
    def actors_help(self) -> EntitiesHelp:
        return self[4]

    @property
    def suite_reporters_help(self) -> EntitiesHelp:
        return self[5]

    @property
    def types_help(self) -> EntitiesHelp:
        return self[6]

    @property
    def entities(self) -> dict:
        """
        entity-name -> EntitiesHelp

        :return: str -> :class:`EntitiesHelp`
        """
        return self[7]

    @property
    def entity_name_2_entity_configuration(self) -> dict:
        """
        entity-name -> EntityConfiguration

        :return: str -> :class:`EntityConfiguration`
        """
        return self[8]
