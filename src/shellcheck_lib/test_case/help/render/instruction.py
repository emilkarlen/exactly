from shellcheck_lib.general.textformat.structure import document as doc, lists
from shellcheck_lib.general.textformat.structure.core import Text
from shellcheck_lib.general.textformat.structure.paragraph import para
from shellcheck_lib.test_case.help.instruction_description import Description, InvokationVariant


def instruction_man_page(description: Description) -> doc.SectionContents:
    todo_para = para('TODO test-case help for instruction ' + description.instruction_name())
    single_line_description_para = para(description.single_line_description())
    main_description_rest = description.main_description_rest()

    sections = _invokation_variants_sections(description.invokation_variants())
    return doc.SectionContents([todo_para,
                                single_line_description_para] +
                               main_description_rest,
                               sections)


def instruction_set_list_item(description: Description) -> lists.HeaderValueListItem:
    description_para = para(description.single_line_description())
    return lists.HeaderValueListItem(Text(description.instruction_name()),
                                     [description_para])


def _invokation_variants_sections(invokation_variants: list) -> list:
    def variants_list():
        items = []
        for invokation_variant in invokation_variants:
            assert isinstance(invokation_variant, InvokationVariant)
            items.append(lists.HeaderValueListItem(Text(invokation_variant.syntax),
                                                   invokation_variant.description_rest))
        return lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                     items)

    if not invokation_variants:
        return []
    return [doc.Section(Text('INVOKATION VARIANTS'),
                        doc.SectionContents([variants_list()],
                                            []))]
