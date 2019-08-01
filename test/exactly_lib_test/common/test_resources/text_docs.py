from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer, \
    structure_assertions as asrt_struct


def is_single_pre_formatted_text(text: ValueAssertion[str]) -> ValueAssertion[TextRenderer]:
    return asrt_renderer.is_renderer_of_major_blocks(
        asrt.matches_sequence([
            asrt_struct.matches_major_block__w_plain_properties(
                asrt.matches_sequence([
                    asrt_struct.matches_minor_block__w_plain_properties(
                        asrt.matches_sequence([
                            asrt_struct.matches_line_element__w_plain_properties(
                                asrt_struct.is_pre_formatted_string(
                                    string=text
                                )
                            )
                        ])
                    )
                ])
            )
        ])
    )
