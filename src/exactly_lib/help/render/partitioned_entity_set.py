from typing import List, Callable, Iterable

from exactly_lib.help.contents_structure.entity import HtmlDocHierarchyGeneratorGetter, CliListConstructorGetter, \
    EntityDocumentation
from exactly_lib.help.render import entities_list_renderer
from exactly_lib.help.render.entity_docs import EntitiesListConstructor
from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor, \
    SectionConstructor, \
    ArticleContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class PartitionNamesSetup:
    def __init__(self,
                 local_target_name: str,
                 header: str,
                 ):
        self.local_target_name = local_target_name
        self.header = header


class PartitionSetup:
    def __init__(self,
                 partition_names_setup: PartitionNamesSetup,
                 filter_entity_docs: Callable[[Iterable[EntityDocumentation]], List[EntityDocumentation]],
                 ):
        self.partition_names_setup = partition_names_setup
        self.filter_entity_docs = filter_entity_docs


class EntitiesPartition:
    def __init__(self,
                 partition_names_setup: PartitionNamesSetup,
                 entity_doc_list: List[EntityDocumentation],
                 ):
        self.partition_names_setup = partition_names_setup
        self.entity_doc_list = entity_doc_list


def partition_entities(partitions_setup: Iterable[PartitionSetup],
                       entity_doc_list: Iterable[EntityDocumentation]) -> List[EntitiesPartition]:
    ret_val = []
    for partition_setup in partitions_setup:
        entity_docs_in_partition = partition_setup.filter_entity_docs(entity_doc_list)
        if entity_docs_in_partition:
            ret_val.append(EntitiesPartition(partition_setup.partition_names_setup,
                                             entity_docs_in_partition))
    return ret_val


class PartitionedCliListConstructorGetter(CliListConstructorGetter):
    def __init__(self,
                 partition_setup_list: Iterable[PartitionSetup],
                 entity_2_summary_paragraphs: Callable[[EntityDocumentation], List[ParagraphItem]]
                 ):
        self.partition_setup_list = partition_setup_list
        self.entity_2_summary_paragraphs = entity_2_summary_paragraphs

    def get_constructor(self, all_entity_doc_list: Iterable[EntityDocumentation]) -> SectionContentsConstructor:
        partitions = partition_entities(self.partition_setup_list, all_entity_doc_list)

        def section_constructor(partition: EntitiesPartition) -> SectionConstructor:
            return sections.section(
                docs.text(partition.partition_names_setup.header),
                EntitiesListConstructor(self.entity_2_summary_paragraphs,
                                        partition.entity_doc_list))

        return sections.contents(sub_sections=map(section_constructor, partitions))


class PartitionedHierarchyGeneratorGetter(HtmlDocHierarchyGeneratorGetter):
    def __init__(self,
                 entity_type_identifier: str,
                 partition_setup_list: Iterable[PartitionSetup],
                 entity_2_article_contents_renderer: Callable[[EntityDocumentation], ArticleContentsConstructor]
                 ):
        self.entity_type_identifier = entity_type_identifier
        self.partition_setup_list = partition_setup_list
        self.entity_2_article_contents_renderer = entity_2_article_contents_renderer

    def get_hierarchy_generator(self,
                                header: str,
                                all_entity_doc_list: List[EntityDocumentation]
                                ) -> generator.SectionHierarchyGenerator:
        def section_hierarchy_node(partition: EntitiesPartition) -> SectionHierarchyGenerator:
            return h.child(partition.partition_names_setup.local_target_name,
                           entities_list_renderer.entity_list_hierarchy(
                               self.entity_type_identifier,
                               self.entity_2_article_contents_renderer,
                               partition.partition_names_setup.header,
                               partition.entity_doc_list,
                           ))

        partitions = partition_entities(self.partition_setup_list, all_entity_doc_list)

        return h.hierarchy(
            docs.string_text(header),
            children=[
                section_hierarchy_node(partition)
                for partition in partitions
            ]
        )
