"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""
from typing import List, Callable, Iterable

from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId, EntityTypeNames
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor, \
    ArticleContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import Text, StringText


class EntityDocumentation:
    """
    Base class for documentation of "entities" with a name and single-line-description.
    """

    def __init__(self, name_and_cross_ref_target: SingularNameAndCrossReferenceId):
        self._name_and_cross_ref_target = name_and_cross_ref_target

    @property
    def name_and_cross_ref_target(self) -> SingularNameAndCrossReferenceId:
        return self._name_and_cross_ref_target

    def singular_name(self) -> str:
        return self._name_and_cross_ref_target.singular_name

    @property
    def singular_name_text(self) -> StringText:
        return self.name_and_cross_ref_target.singular_name_text

    def single_line_description_str(self) -> str:
        return self._name_and_cross_ref_target.single_line_description_str

    def cross_reference_target(self) -> CrossReferenceId:
        return self._name_and_cross_ref_target.cross_reference_target

    def single_line_description(self) -> Text:
        return docs.text(self.single_line_description_str())

    def name_and_single_line_description(self) -> Text:
        return docs.text(self.name_and_single_line_description_str())

    def name_and_single_line_description_str(self) -> str:
        return formatting.entity(self.singular_name()) + ' - ' + self.single_line_description_str()


class EntityTypeHelp(tuple):
    def __new__(cls,
                names: EntityTypeNames,
                entities: Iterable[EntityDocumentation]):
        return tuple.__new__(cls, (names,
                                   list(entities)))

    @property
    def names(self) -> EntityTypeNames:
        return self[0]

    @property
    def all_entities(self) -> List[EntityDocumentation]:
        return self[1]


class HtmlDocHierarchyGeneratorGetter:
    def get_hierarchy_generator(self,
                                header: str,
                                all_entity_doc_list: List[EntityDocumentation]) -> SectionHierarchyGenerator:
        raise NotImplementedError('abstract method')


class CliListConstructorGetter:
    def get_constructor(self, all_entity_doc_list: List[EntityDocumentation]) -> SectionContentsConstructor:
        raise NotImplementedError('abstract method')


class EntityTypeConfiguration(tuple):
    def __new__(cls,
                entities_help: EntityTypeHelp,
                entity_doc_2_article_contents_renderer: Callable[[EntityDocumentation], ArticleContentsConstructor],
                cli_list_renderer_getter: CliListConstructorGetter,
                html_doc_generator_getter: HtmlDocHierarchyGeneratorGetter):
        return tuple.__new__(cls, (entities_help,
                                   entity_doc_2_article_contents_renderer,
                                   cli_list_renderer_getter,
                                   html_doc_generator_getter))

    @property
    def entities_help(self) -> EntityTypeHelp:
        return self[0]

    @property
    def entity_doc_2_article_contents_renderer(self) -> Callable[[EntityDocumentation], ArticleContentsConstructor]:
        return self[1]

    @property
    def cli_list_constructor_getter(self) -> CliListConstructorGetter:
        return self[2]

    @property
    def html_doc_generator_getter(self) -> HtmlDocHierarchyGeneratorGetter:
        return self[3]

    def get_hierarchy_generator(self, header: str) -> SectionHierarchyGenerator:
        return self.html_doc_generator_getter.get_hierarchy_generator(header, self.entities_help.all_entities)
