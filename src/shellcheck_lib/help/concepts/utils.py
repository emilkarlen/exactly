from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.structures import text, SEPARATION_OF_HEADER_AND_CONTENTS


def sorted_concepts_list(concepts: iter) -> ParagraphItem:
    all_cps = sorted(concepts, key=lambda cd: cd.name().singular)
    items = [lists.HeaderContentListItem(text(cp.name().singular),
                                         cp.summary_paragraphs())
             for cp in all_cps]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))
