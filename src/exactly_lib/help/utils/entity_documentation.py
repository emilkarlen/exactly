"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""
import types

from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.cross_reference_id import CustomTargetInfoFactory, CrossReferenceId
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import Text, ParagraphItem
from exactly_lib.util.textformat.structure.structures import SEPARATION_OF_HEADER_AND_CONTENTS


class EntityDocumentation:
    """
    Base class for documentation of "entities" with a name and single-line-description.
    """

    def singular_name(self) -> str:
        """
        Name of the entity in singular.
        """
        raise NotImplementedError()

    def single_line_description(self) -> Text:
        """
        A short description of the entity.
        """
        raise NotImplementedError()

    def cross_reference_target(self) -> CrossReferenceId:
        raise NotImplementedError()


def sorted_entity_list(entities: list) -> list:
    return sorted(entities, key=lambda ed: ed.singular_name())


class AllEntitiesListRenderer(SectionContentsRenderer):
    def __init__(self, all_entities: list):
        self.all_entities = all_entities

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents([_sorted_entities_list(self.all_entities)], [])


class HtmlDocGeneratorForEntitiesHelp:
    def __init__(self,
                 entity_2_section_contents_renderer: types.FunctionType,
                 all_entities: list,
                 rendering_environment: RenderingEnvironment,
                 ):
        """

        :param entity_2_section_contents_renderer: EntityDocumentation -> SectionContentsRenderer
        :param rendering_environment:
        :param all_entities:
        """
        self.entity_2_section_contents_renderer = entity_2_section_contents_renderer
        self.all_entities = all_entities
        self.rendering_environment = rendering_environment

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        ret_val_sections = []
        ret_val_targets = []
        for entity in sorted_entity_list(self.all_entities):
            assert isinstance(entity, EntityDocumentation)
            actor_presentation_str = entity.singular_name()
            header = docs.anchor_text(docs.text(actor_presentation_str),
                                      entity.cross_reference_target())
            section_contents_renderer = self.entity_2_section_contents_renderer(entity)
            assert isinstance(section_contents_renderer, SectionContentsRenderer)
            section = doc.Section(header,
                                  section_contents_renderer.apply(self.rendering_environment))
            target_info_node = cross_ref.TargetInfoNode(cross_ref.TargetInfo(actor_presentation_str,
                                                                             entity.cross_reference_target()),
                                                        [])
            ret_val_sections.append(section)
            ret_val_targets.append(target_info_node)
        return ret_val_targets, doc.SectionContents([], ret_val_sections)


def _sorted_entities_list(entities: iter) -> ParagraphItem:
    items = [lists.HeaderContentListItem(docs.text(entity.singular_name()),
                                         docs.paras(entity.single_line_description()))
             for entity in (sorted_entity_list(entities))]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))
