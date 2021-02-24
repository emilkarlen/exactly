from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.util.render.renderer import Renderer
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches(message: Assertion[TextRenderer]) -> Assertion[ErrorMessageWithFixTip]:
    return asrt.is_instance_with(
        ErrorMessageWithFixTip,
        asrt.and_([
            asrt.sub_component('message',
                               ErrorMessageWithFixTip.message.fget,
                               message),
            asrt.sub_component('how_to_fix',
                               ErrorMessageWithFixTip.how_to_fix.fget,
                               asrt.is_none_or_instance_with(Renderer, asrt_text_doc.is_any_text())),
        ])
    )
