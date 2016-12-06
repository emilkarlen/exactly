from exactly_lib.common.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.util.textformat.structure import document as doc, paragraph, lists
from exactly_lib.util.textformat.structure.structures import para, text

LIST_INDENT = 2

BLANK_LINE_BETWEEN_ELEMENTS = lists.Separations(1, 0)


def variants_list(instruction_name: str,
                  invokation_variants: list,
                  indented: bool = False,
                  custom_separations: lists.Separations = None) -> paragraph.ParagraphItem:
    title_prefix = instruction_name + ' ' if instruction_name else ''
    items = []
    for x in invokation_variants:
        assert isinstance(x, InvokationVariant)
        items.append(lists.HeaderContentListItem(text(title_prefix + x.syntax),
                                                 x.description_rest))
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=_custom_list_indent(indented),
                                                custom_separations=custom_separations))


def invokation_variants_content(instruction_name_or_none: str,
                                invokation_variants: list,
                                syntax_element_descriptions: list
                                ) -> doc.SectionContents:
    def syntax_element_description_list() -> paragraph.ParagraphItem:
        items = []
        for x in syntax_element_descriptions:
            assert isinstance(x, SyntaxElementDescription)
            variants_list_paragraphs = []
            if x.invokation_variants:
                variants_list_paragraphs = [para('Forms:'),
                                            variants_list(None,
                                                          x.invokation_variants,
                                                          True,
                                                          custom_separations=BLANK_LINE_BETWEEN_ELEMENTS)]
            items.append(lists.HeaderContentListItem(text(x.element_name),
                                                     x.description_rest +
                                                     variants_list_paragraphs))
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_indent_spaces=_custom_list_indent(True),
                                                    custom_separations=BLANK_LINE_BETWEEN_ELEMENTS))

    def syntax_element_description_paragraph_items() -> list:
        if not syntax_element_descriptions:
            return []
        return [para('where'),
                syntax_element_description_list()
                ]

    return doc.SectionContents([variants_list(instruction_name_or_none,
                                              invokation_variants,
                                              custom_separations=BLANK_LINE_BETWEEN_ELEMENTS)] +
                               syntax_element_description_paragraph_items(),
                               [])


def _custom_list_indent(indented: bool) -> int:
    return None if indented else 0
