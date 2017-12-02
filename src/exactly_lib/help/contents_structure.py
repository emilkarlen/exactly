from exactly_lib.help.program_modes.main_program.contents_structure import MainProgramHelp
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.utils.entity_documentation import EntitiesHelp
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionHierarchyGenerator
from exactly_lib.util.textformat.building.section_contents_renderer import SectionContentsRenderer


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
                entity_doc_2_article_contents_renderer,
                cli_list_renderer_getter: CliListRendererGetter,
                html_doc_generator_getter: HtmlDocHierarchyGeneratorGetter):
        return tuple.__new__(cls, (entities_help,
                                   entity_doc_2_article_contents_renderer,
                                   cli_list_renderer_getter,
                                   html_doc_generator_getter))

    @property
    def entities_help(self) -> EntitiesHelp:
        return self[0]

    @property
    def entity_doc_2_article_contents_renderer(self):
        """
        :rtype: `EntityDocumentation` -> `ArticleContentsRenderer`
        """
        return self[1]

    @property
    def cli_list_renderer_getter(self) -> CliListRendererGetter:
        return self[2]

    @property
    def html_doc_generator_getter(self) -> HtmlDocHierarchyGeneratorGetter:
        return self[3]

    def get_hierarchy_generator(self, header: str) -> SectionHierarchyGenerator:
        return self.html_doc_generator_getter.get_hierarchy_generator(header, self.entities_help.all_entities)


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
