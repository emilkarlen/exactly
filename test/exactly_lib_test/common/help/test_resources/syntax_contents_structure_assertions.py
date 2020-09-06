from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources import structure as asrt_struct

is_invokation_variant = asrt.is_instance_with(
    InvokationVariant,
    asrt.And([
        asrt.sub_component('syntax',
                           lambda iv: iv.syntax,
                           asrt.IsInstance(str)),
        asrt.sub_component_sequence('description_rest',
                                    lambda iv: iv.description_rest,
                                    asrt_struct.is_paragraph_item)
    ]))

is_syntax_element_description = asrt.is_instance_with(
    SyntaxElementDescription,
    asrt.And([
        asrt.sub_component('name',
                           lambda sed: sed.element_name,
                           asrt.IsInstance(str)),
        asrt.sub_component_sequence('before_invokation_variants',
                                    lambda sed: sed.before_invokation_variants,
                                    asrt_struct.is_paragraph_item),
        asrt.sub_component_sequence('after_invokation_variants',
                                    lambda sed: sed.after_invokation_variants,
                                    asrt_struct.is_paragraph_item),
        asrt.sub_component_sequence('invokation_variants',
                                    lambda sed: sed.invokation_variants,
                                    is_invokation_variant)
    ]))
