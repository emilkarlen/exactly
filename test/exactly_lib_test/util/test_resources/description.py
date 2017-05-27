from exactly_lib.util.description import Description, DescriptionWithSubSections
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources import structure as struct_check

is_description = asrt.And([
    asrt.IsInstance(Description),
    asrt.sub_component(
        'single line description',
        Description.single_line_description.fget,
        struct_check.is_text),
    asrt.sub_component_list(
        'rest paragraph-items',
        Description.rest.fget,
        struct_check.is_paragraph_item),
])

is_description_with_sub_sections = asrt.And([
    asrt.IsInstance(DescriptionWithSubSections),
    asrt.sub_component(
        'single line description',
        DescriptionWithSubSections.single_line_description.fget,
        struct_check.is_text),
    asrt.sub_component_list(
        'rest sub-sections',
        DescriptionWithSubSections.rest.fget,
        struct_check.is_section_contents),
])
