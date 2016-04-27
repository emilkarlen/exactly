from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure import structures as docs


def sorted_concepts_list(concepts: iter) -> ParagraphItem:
    all_cps = sorted(concepts, key=lambda cd: cd.name().singular)
    items = [lists.HeaderContentListItem(docs.cross_reference(cp.name().singular,
                                                              cp.cross_reference_target(),
                                                              allow_rendering_of_visible_extra_target_text=False),
                                         cp.summary_paragraphs())
             for cp in all_cps]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0,
                                                custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS))
