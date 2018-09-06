from typing import List, Sequence

from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem, TextSeeAlsoItem, SeeAlsoItemVisitor, \
    SeeAlsoSet, SeeAlsoItem
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.help.render.cross_reference import CrossReferenceTextConstructor
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text
from exactly_lib.util.textformat.utils import append_section_if_contents_is_non_empty

SEE_ALSO_TITLE = docs.text('See also')
SEE_ALSO_TITLE__UPPERCASE = docs.text('SEE ALSO')


def see_also_items_paragraph(see_also_items: List[SeeAlsoItem],
                             environment: ConstructionEnvironment) -> ParagraphItem:
    """
    :return: A ParagraphItem that displays a list of `SeeAlsoItem`s.
    """
    renderer = _Renderer(environment.cross_ref_text_constructor)
    return docs.simple_header_only_list([renderer.visit(see_also_item)
                                         for see_also_item in see_also_items],
                                        lists.ListType.ITEMIZED_LIST)


def see_also_items_paragraphs(see_also_items: List[SeeAlsoItem],
                              environment: ConstructionEnvironment) -> List[ParagraphItem]:
    """
    :return: [] if no `SeeAlsoItem`s, else a single paragraph
    """
    if not see_also_items:
        return []
    return [see_also_items_paragraph(see_also_items, environment)]


def see_also_sections(see_also_targets: Sequence[SeeAlsoTarget],
                      rendering_environment: ConstructionEnvironment,
                      uppercase_title: bool = False) -> List[docs.SectionItem]:
    """
    :return: An empty list if no targets, otherwise a singleton list.
    """
    ret_val = []
    title = SEE_ALSO_TITLE__UPPERCASE if uppercase_title else SEE_ALSO_TITLE
    append_section_if_contents_is_non_empty(
        ret_val,
        title,
        see_also_items_paragraphs(SeeAlsoSet(see_also_targets).see_also_items,
                                  rendering_environment))
    return ret_val


class _Renderer(SeeAlsoItemVisitor):
    def __init__(self, cross_ref_text_constructor: CrossReferenceTextConstructor):
        self.cross_ref_text_constructor = cross_ref_text_constructor

    def visit_cross_reference_id(self, x: CrossReferenceIdSeeAlsoItem) -> Text:
        return self.cross_ref_text_constructor.apply(x.cross_reference_id)

    def visit_text(self, x: TextSeeAlsoItem) -> Text:
        return x.text
