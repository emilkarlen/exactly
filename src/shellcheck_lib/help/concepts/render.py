from shellcheck_lib.help.program_modes.test_case.contents_structure import ConceptsHelp
from shellcheck_lib.help.utils.render import SectionContentsRenderer
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.structures import text, para, SEPARATION_OF_HEADER_AND_CONTENTS


class AllConceptsListRenderer(SectionContentsRenderer):
    def __init__(self, concepts_help: ConceptsHelp):
        self.concepts_help = concepts_help

    def apply(self) -> doc.SectionContents:
        return doc.SectionContents([sorted_concepts_list(self.concepts_help.all_concepts)], [])


def sorted_concepts_list(concepts: iter) -> ParagraphItem:
    all_cps = sorted(concepts, key=lambda cd: cd.name().singular)
    items = [lists.HeaderContentListItem(text(cp.name().singular),
                                         [para(cp.purpose().single_line_description)])
             for cp in all_cps]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))
