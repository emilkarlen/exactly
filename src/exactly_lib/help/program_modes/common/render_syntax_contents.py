from typing import Iterable, List, Sequence, Optional

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions import doc_format
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.help import std_tags
from exactly_lib.util.textformat.structure import document as doc, lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem

_SYNTAX_LINE_TAGS = frozenset([std_tags.SYNTAX_TEXT])

LIST_INDENT = 2

BLANK_LINE_BETWEEN_ELEMENTS = lists.Separations(1, 0)


def variants_list(instruction_name: str,
                  invokation_variants: Iterable[InvokationVariant],
                  indented: bool = False,
                  custom_separations: lists.Separations = None) -> ParagraphItem:
    title_prefix = instruction_name + ' ' if instruction_name else ''
    items = []
    for x in invokation_variants:
        assert isinstance(x, InvokationVariant)
        title = title_prefix + x.syntax
        items.append(docs.list_item(syntax_text(title),
                                    list(x.description_rest)))
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=_custom_list_indent(indented),
                                                custom_separations=custom_separations))


def invokation_variants_paragraphs(instruction_name_or_none: str,
                                   invokation_variants: Sequence[InvokationVariant],
                                   syntax_element_descriptions: Iterable[SyntaxElementDescription]
                                   ) -> List[ParagraphItem]:
    def syntax_element_description_list() -> ParagraphItem:
        items = []
        for x in syntax_element_descriptions:
            assert isinstance(x, SyntaxElementDescription)
            variants_list_paragraphs = []
            if x.invokation_variants:
                variants_list_paragraphs = [variants_list(None,
                                                          x.invokation_variants,
                                                          True,
                                                          custom_separations=BLANK_LINE_BETWEEN_ELEMENTS)]
            separator_paras = [FORMS_PARA] if x.invokation_variants and x.description_rest else []
            contents = list(x.description_rest) + separator_paras + variants_list_paragraphs
            items.append(docs.list_item(syntax_text(x.element_name),
                                        contents))
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_indent_spaces=_custom_list_indent(True),
                                                    custom_separations=BLANK_LINE_BETWEEN_ELEMENTS))

    def syntax_element_description_paragraph_items() -> List[ParagraphItem]:
        if not syntax_element_descriptions:
            return []
        return [_WHERE_PARA,
                syntax_element_description_list()
                ]

    if not invokation_variants:
        return []
    return ([variants_list(instruction_name_or_none,
                           invokation_variants,
                           custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS)] +
            syntax_element_description_paragraph_items())


def invokation_variants_content(instruction_name: Optional[str],
                                invokation_variants: Sequence[InvokationVariant],
                                syntax_element_descriptions: Iterable[SyntaxElementDescription]
                                ) -> doc.SectionContents:
    return doc.SectionContents(invokation_variants_paragraphs(instruction_name,
                                                              invokation_variants,
                                                              syntax_element_descriptions
                                                              ),
                               [])


_WHERE_PARA = docs.para(doc_format.text_as_header('where'))
FORMS_PARA = docs.para(doc_format.text_as_header('Forms:'))


def _custom_list_indent(indented: bool) -> int:
    return None if indented else 0
