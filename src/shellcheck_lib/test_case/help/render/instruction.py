from shellcheck_lib.general.textformat.structure import document as doc, paragraph, lists
from shellcheck_lib.general.textformat.structure.core import Text
from shellcheck_lib.general.textformat.structure.paragraph import para
from shellcheck_lib.test_case.help.instruction_description import Description, InvokationVariant, \
    SyntaxElementDescription


def instruction_man_page(description: Description) -> doc.SectionContents:
    prelude_paragraphs = [(para('TODO test-case help for instruction ' + description.instruction_name())),
                          (para(description.single_line_description()))]
    main_description_rest = description.main_description_rest()
    if description.invokation_variants():
        section_contents = _invokation_variants_content(description)
        return doc.SectionContents(prelude_paragraphs,
                                   [doc.Section(Text('INVOKATION VARIANTS'),
                                                section_contents),
                                    doc.Section(Text('DESCRIPTION'),
                                                doc.SectionContents(main_description_rest,
                                                                    []))])
    else:
        return doc.SectionContents(prelude_paragraphs +
                                   main_description_rest,
                                   [])


def instruction_set_list_item(description: Description) -> lists.HeaderValueListItem:
    description_para = para(description.single_line_description())
    return lists.HeaderValueListItem(Text(description.instruction_name()),
                                     [description_para])


def _invokation_variants_content(description: Description) -> doc.SectionContents:
    def variants_list(invokation_variants: list) -> paragraph.ParagraphItem:
        items = []
        for x in invokation_variants:
            assert isinstance(x, InvokationVariant)
            items.append(lists.HeaderValueListItem(Text(x.syntax),
                                                   x.description_rest))
        return lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                     items)

    def syntax_element_description_list() -> paragraph.ParagraphItem:
        items = []
        for x in description.syntax_element_descriptions():
            assert isinstance(x, SyntaxElementDescription)
            variants_list_paragraphs = []
            if x.invokation_variants:
                variants_list_paragraphs = [para('where'),
                                            variants_list(x.invokation_variants)]
            items.append(lists.HeaderValueListItem(Text(x.element_name),
                                                   x.description_rest +
                                                   variants_list_paragraphs))
        return lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                     items)

    def syntax_element_description_sections() -> list:
        if not description.syntax_element_descriptions():
            return []
        return [doc.Section(Text('where'),
                            doc.SectionContents([syntax_element_description_list()],
                                                []))
                ]

    return doc.SectionContents([variants_list(description.invokation_variants())],
                               syntax_element_description_sections())
