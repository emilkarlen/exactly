import unittest
from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.simple_textstruct.test_resources import render_to_str
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_struct


def new_single_string_text_for_test(text: str) -> TextRenderer:
    return text_docs.single_pre_formatted_line_object(text)


def new_single_string_text_for_test__optional(text: Optional[str]) -> Optional[TextRenderer]:
    return (None
            if text is None
            else text_docs.single_pre_formatted_line_object(text)
            )


def is_single_pre_formatted_text_that_equals(text: str) -> ValueAssertion[TextRenderer]:
    return is_single_pre_formatted_text(asrt.equals(text))


def is_string_for_test(text: ValueAssertion[str]) -> ValueAssertion[TextRenderer]:
    return is_single_pre_formatted_text(text)


def is_string_for_test_that_equals(text: str) -> ValueAssertion[TextRenderer]:
    return is_string_for_test(asrt.equals(text))


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


def is_any_text() -> ValueAssertion[TextRenderer]:
    return _IS_ANY_TEXT


def assert_is_valid_text_renderer(put: unittest.TestCase,
                                  actual):
    is_any_text().apply_without_message(put, actual)


def rendered_text_matches(text: ValueAssertion[str]) -> ValueAssertion[TextRenderer]:
    return asrt_renderer.is_renderer_of_major_blocks(
        asrt.on_transformed(render_to_str.print_major_blocks,
                            text)
    )


_IS_ANY_TEXT = asrt_renderer.is_renderer_of_major_blocks()
