from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation, \
    InvokationVariant, \
    SyntaxElementDescription
from shellcheck_lib.help.utils.render import SectionContentsRenderer
from shellcheck_lib.util.textformat.structure import document as doc, paragraph, lists
from shellcheck_lib.util.textformat.structure.structures import para, text, section

LIST_INDENT = 2


class InstructionManPageRenderer(SectionContentsRenderer):
    def __init__(self, documentation: InstructionDocumentation):
        self.documentation = documentation

    def apply(self) -> doc.SectionContents:
        description = self.documentation
        sub_sections = []
        if description.invokation_variants():
            sub_sections.append(doc.Section(text('SYNOPSIS'),
                                            _invokation_variants_content(description)))
        main_description_rest = description.main_description_rest()
        if main_description_rest:
            sub_sections.append(section('DESCRIPTION',
                                        main_description_rest))
        cross_references = description.cross_references()
        if cross_references:
            sub_sections.append(section('SEE ALSO',
                                        [para('TODO cross references')]))
        prelude_paragraphs = [para(description.single_line_description())]
        return doc.SectionContents(prelude_paragraphs,
                                   sub_sections)


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
