from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources import structure as asrt_struct

is_invokation_variant = asrt.is_instance_with(
    InvokationVariant,
    asrt.And([
        asrt.sub_component('syntax',
                           lambda x: x.syntax,
                           asrt.IsInstance(str)),
        asrt.sub_component_list('description_rest',
                                lambda x: x.description_rest,
                                asrt_struct.is_paragraph_item)
    ]))

is_syntax_element_description = asrt.is_instance_with(
    SyntaxElementDescription,
    asrt.And([
        asrt.sub_component('name',
                           lambda x: x.element_name,
                           asrt.IsInstance(str)),
        asrt.sub_component_list('description_rest',
                                lambda x: x.description_rest,
                                asrt_struct.is_paragraph_item),
        asrt.sub_component_list('invokation_variants',
                                lambda sed: sed.invokation_variants,
                                is_invokation_variant)
    ]))
