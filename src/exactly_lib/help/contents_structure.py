from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.utils.entity_documentation import EntitiesHelp
from exactly_lib.help.utils.rendering.section_contents_renderer import SectionContentsRenderer
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionHierarchyGenerator


class HtmlDocHierarchyGeneratorGetter:
    def get_hierarchy_generator(self,
                                header: str,
                                all_entity_doc_list: list) -> SectionHierarchyGenerator:
        raise NotImplementedError('abstract method')


class CliListRendererGetter:
    def get_render(self, all_entity_doc_list: list) -> SectionContentsRenderer:
        raise NotImplementedError('abstract method')


class EntityConfiguration(tuple):
    def __new__(cls,
                entities_help: EntitiesHelp,
                entity_doc_2_section_contents_renderer,
                cli_list_renderer_getter: CliListRendererGetter):
        return tuple.__new__(cls, (entities_help,
                                   entity_doc_2_section_contents_renderer,
                                   cli_list_renderer_getter))

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
    def cli_list_renderer_getter(self) -> CliListRendererGetter:
        """
        :rtype: Iterable[ElementDocumentation] -> :class:`CliListRendererGetter`
        """
        return self[2]


class ApplicationHelp(tuple):
    def __new__(cls,
                main_program_help: MainProgramHelp,
                test_case_help: TestCaseHelp,
                test_suite_help: TestSuiteHelp,
                entity_name_2_entity_configuration: dict = ()):
        """
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

    def entity_conf_for(self, entity_type_name: str) -> EntityConfiguration:
        return self.entity_name_2_entity_configuration[entity_type_name]

    @property
    def entity_name_2_entity_configuration(self) -> dict:
        """
        entity-name -> EntityConfiguration

        :return: str -> :class:`EntityConfiguration`
        """
        return self[3]
