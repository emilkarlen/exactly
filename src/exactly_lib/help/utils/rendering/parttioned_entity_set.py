import types

import exactly_lib.util.textformat.construction.section_hierarchy_con
from exactly_lib.help.contents_structure import HtmlDocHierarchyGeneratorGetter, CliListConstructorGetter
from exactly_lib.help.html_doc.parts.utils import entities_list_renderer
from exactly_lib.help.utils.rendering.entity_docs import AllEntitiesListConstructor
from exactly_lib.util.textformat.construction import section_hierarchy_constructor
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    SectionConstructor, \
    SectionConstructorFromSectionContentsConstructor, section_contents_constructor_with_sub_sections
from exactly_lib.util.textformat.structure import structures as docs


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
                 filter_entity_docs: types.FunctionType,
                 ):
        self.partition_names_setup = partition_names_setup
        self.filter_entity_docs = filter_entity_docs


class EntitiesPartition:
    def __init__(self,
                 partition_names_setup: PartitionNamesSetup,
                 entity_doc_list: list,
                 ):
        self.partition_names_setup = partition_names_setup
        self.entity_doc_list = entity_doc_list


def partition_entities(partitions_setup: list, entity_doc_list: list) -> list:
    """
    :type partitions_setup: list of :class:`PartitionSetup`
    :rtype: list of :class:`EntitiesPartition`
    """
    ret_val = []
    for partition_setup in partitions_setup:
        entity_docs_in_partition = partition_setup.filter_entity_docs(entity_doc_list)
        if entity_docs_in_partition:
            ret_val.append(EntitiesPartition(partition_setup.partition_names_setup,
                                             entity_docs_in_partition))
    return ret_val


def list_render(partition_setup_list: list,
                entity_2_summary_paragraphs: types.FunctionType,
                type_doc_list: list) -> SectionContentsConstructor:
    partitions = partition_entities(partition_setup_list, type_doc_list)

    def section_renderer(partition: EntitiesPartition) -> SectionConstructor:
        return SectionConstructorFromSectionContentsConstructor(
            docs.text(partition.partition_names_setup.header),
            AllEntitiesListConstructor(
                entity_2_summary_paragraphs,
                partition.entity_doc_list))

    return section_contents_constructor_with_sub_sections(list(
        map(section_renderer, partitions)
    ))


class PartitionedCliListConstructorGetter(CliListConstructorGetter):
    def __init__(self,
                 partition_setup_list: list,
                 entity_2_summary_paragraphs: types.FunctionType
                 ):
        self.partition_setup_list = partition_setup_list
        self.entity_2_summary_paragraphs = entity_2_summary_paragraphs

    def get_render(self, all_entity_doc_list: list) -> SectionContentsConstructor:
        partitions = partition_entities(self.partition_setup_list, all_entity_doc_list)

        def section_renderer(partition: EntitiesPartition) -> SectionConstructor:
            return SectionConstructorFromSectionContentsConstructor(
                docs.text(partition.partition_names_setup.header),
                AllEntitiesListConstructor(
                    self.entity_2_summary_paragraphs,
                    partition.entity_doc_list))

        return section_contents_constructor_with_sub_sections(list(
            map(section_renderer, partitions)
        ))


class PartitionedHierarchyGeneratorGetter(HtmlDocHierarchyGeneratorGetter):
    def __init__(self,
                 entity_type_identifier: str,
                 partition_setup_list: list,
                 entity_2_article_contents_renderer: types.FunctionType
                 ):
        self.entity_type_identifier = entity_type_identifier
        self.partition_setup_list = partition_setup_list
        self.entity_2_article_contents_renderer = entity_2_article_contents_renderer

    def get_hierarchy_generator(self,
                                header: str,
                                all_entity_doc_list: list
                                ) -> section_hierarchy_constructor.SectionHierarchyGenerator:
        def section_hierarchy_node(partition: EntitiesPartition) -> tuple:
            return (partition.partition_names_setup.local_target_name,
                    entities_list_renderer.HtmlDocHierarchyGeneratorForEntitiesHelp(
                        self.entity_type_identifier,
                        partition.partition_names_setup.header,
                        self.entity_2_article_contents_renderer,
                        partition.entity_doc_list,
                    ))

        partitions = partition_entities(self.partition_setup_list, all_entity_doc_list)

        return exactly_lib.util.textformat.construction.section_hierarchy_con.parent(
            header,
            [],
            [
                section_hierarchy_node(partition)
                for partition in partitions
            ]
        )
