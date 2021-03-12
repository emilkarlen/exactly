from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def is_success() -> Assertion[Optional[TextRenderer]]:
    return asrt.ValueIsNone()


def is_failure() -> Assertion[Optional[TextRenderer]]:
    return asrt_renderer.is_renderer_of_major_blocks()