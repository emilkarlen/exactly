from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation, \
    InvokationVariant, \
    SyntaxElementDescription
from shellcheck_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from shellcheck_lib.util.textformat.structure import document as doc, paragraph, lists
from shellcheck_lib.util.textformat.structure.structures import para, text, section, simple_header_only_list

LIST_INDENT = 2

BLANK_LINE_BETWEEN_ELEMENTS = lists.Separations(1, 0)


class InstructionManPageRenderer(SectionContentsRenderer):
    def __init__(self,
                 documentation: InstructionDocumentation):
        self.documentation = documentation

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        documentation = self.documentation
        sub_sections = []
        if documentation.invokation_variants():
            sub_sections.append(doc.Section(text('SYNOPSIS'),
                                            _invokation_variants_content(documentation)))
        main_description_rest = documentation.main_description_rest()
        if main_description_rest:
            sub_sections.append(section('DESCRIPTION',
                                        main_description_rest))
        cross_references = documentation.cross_references()
        if cross_references:
            cross_reference_list = simple_header_only_list([environment.cross_ref_text_constructor.apply(cross_ref)
                                                            for cross_ref in cross_references],
                                                           lists.ListType.ITEMIZED_LIST)
            sub_sections.append(section('SEE ALSO',
                                        [cross_reference_list]))
        prelude_paragraphs = [para(documentation.single_line_description())]
        return doc.SectionContents(prelude_paragraphs,
                                   sub_sections)


def instruction_set_list_item(description: InstructionDocumentation) -> lists.HeaderContentListItem:
    description_para = para(description.single_line_description())
    return lists.HeaderContentListItem(text(description.instruction_name()),
                                       [description_para])


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


def _invokation_variants_content(instr_doc: InstructionDocumentation) -> doc.SectionContents:
    def syntax_element_description_list() -> paragraph.ParagraphItem:
        items = []
        for x in instr_doc.syntax_element_descriptions():
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
        if not instr_doc.syntax_element_descriptions():
            return []
        return [para('where'),
                syntax_element_description_list()
                ]

    return doc.SectionContents([variants_list(instr_doc.instruction_name(),
                                              instr_doc.invokation_variants(),
                                              custom_separations=BLANK_LINE_BETWEEN_ELEMENTS)] +
                               syntax_element_description_paragraph_items(),
                               [])


def _custom_list_indent(indented: bool) -> int:
    return None if indented else 0
