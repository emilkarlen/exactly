from exactly_lib.util.textformat.structure import core as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs


def toc_list(target_info_hierarchy: list,
             list_type: lists.ListType) -> doc.ParagraphItem:
    items = []
    for node in target_info_hierarchy:
        sub_lists = []
        if node.children:
            sub_lists = [toc_list(node.children, list_type)]
        item = lists.HeaderContentListItem(docs.cross_reference(node.data.presentation_str,
                                                                node.data.target),
                                           sub_lists)
        items.append(item)
    return lists.HeaderContentList(items,
                                   lists.Format(list_type))
