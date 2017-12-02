from exactly_lib.util.textformat.construction.section_hierarchy import TargetInfo
from exactly_lib.util.textformat.structure.core import AnchorText
from exactly_lib_test.help_texts.test_resources import cross_reference_id_va as cross_ref_id_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources.equals_paragraph_item import is_string_text_that_equals
from exactly_lib_test.util.textformat.test_resources.structure import is_anchor_text


def is_anchor_text_that_corresponds_to(expected: TargetInfo) -> asrt.ValueAssertion:
    return asrt.And([
        is_anchor_text,
        asrt.sub_component('anchor',
                           AnchorText.anchor.fget,
                           cross_ref_id_asrt.equals(expected.target)),
        asrt.sub_component('anchored_text',
                           AnchorText.anchored_text.fget,
                           is_string_text_that_equals(expected.presentation_text.value)),
    ])
