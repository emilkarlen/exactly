from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation, \
    InvokationVariant, \
    SyntaxElementDescription
from shellcheck_lib.help.utils.render import SectionContentsRenderer
from shellcheck_lib.util.textformat.structure import document as doc, paragraph, lists
from shellcheck_lib.util.textformat.structure.structures import para, text

LIST_INDENT = 2


class InstructionManPageRenderer(SectionContentsRenderer):
    def __init__(self, documentation: InstructionDocumentation):
        self.documentation = documentation

    def apply(self) -> doc.SectionContents:
        return instruction_man_page(self.documentation)


def instruction_man_page(description: InstructionDocumentation) -> doc.SectionContents:
    prelude_paragraphs = [(para(description.single_line_description()))]
    main_description_rest = description.main_description_rest()
    if description.invokation_variants():
        section_contents = _invokation_variants_content(description)
        description_sections = [] if not main_description_rest else [doc.Section(text('DESCRIPTION'),
                                                                                 doc.SectionContents(
                                                                                     main_description_rest, []))]
        return doc.SectionContents(prelude_paragraphs,
                                   [doc.Section(text('SYNOPSIS'),
                                                section_contents)] +
                                   description_sections)
    else:
        return doc.SectionContents(prelude_paragraphs +
                                   main_description_rest,
                                   [])


def instruction_set_list_item(description: InstructionDocumentation) -> lists.HeaderContentListItem:
    description_para = para(description.single_line_description())
    return lists.HeaderContentListItem(text(description.instruction_name()),
                                       [description_para])


def variants_list(invokation_variants: list,
                  indented: bool = False,
                  custom_separations: lists.Separations = None) -> paragraph.ParagraphItem:
    items = []
    for x in invokation_variants:
        assert isinstance(x, InvokationVariant)
        items.append(lists.HeaderContentListItem(text(x.syntax),
                                                 x.description_rest))
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=_custom_list_indent(indented),
                                                custom_separations=custom_separations))


def _invokation_variants_content(description: InstructionDocumentation) -> doc.SectionContents:
    def syntax_element_description_list() -> paragraph.ParagraphItem:
        blank_line_between_elements = lists.Separations(1, 0)
        items = []
        for x in description.syntax_element_descriptions():
            assert isinstance(x, SyntaxElementDescription)
            variants_list_paragraphs = []
            if x.invokation_variants:
                variants_list_paragraphs = [para('Forms:'),
                                            variants_list(x.invokation_variants,
                                                          True,
                                                          custom_separations=blank_line_between_elements)]
            items.append(lists.HeaderContentListItem(text(x.element_name),
                                                     x.description_rest +
                                                     variants_list_paragraphs))
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_indent_spaces=_custom_list_indent(True),
                                                    custom_separations=blank_line_between_elements))

    def syntax_element_description_paragraph_items() -> list:
        if not description.syntax_element_descriptions():
            return []
        return [para('where'),
                syntax_element_description_list()
                ]

    return doc.SectionContents([variants_list(description.invokation_variants())] +
                               syntax_element_description_paragraph_items(),
                               [])


def _custom_list_indent(indented: bool) -> int:
    return None if indented else 0
