from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc


def hard_error_ex(err_msg: str) -> HardErrorException:
    return HardErrorException(
        asrt_text_doc.new_pre_formatted_str_for_test(err_msg)
    )
