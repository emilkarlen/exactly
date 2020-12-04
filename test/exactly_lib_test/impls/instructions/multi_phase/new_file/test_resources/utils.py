from enum import Enum

from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.types.test_resources import validation
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Step(Enum):
    VALIDATE_PRE_SDS = 1
    MAIN = 2


IS_FAILURE_OF_VALIDATION = validation.is_arbitrary_validation_failure()
IS_FAILURE = asrt_text_doc.is_any_text()
IS_SUCCESS = asrt.is_none
