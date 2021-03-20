from typing import Optional, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.actions import do_nothing
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationActual


class DdvValidatorThat(DdvValidator):
    def __init__(self,
                 pre_sds_action: Callable[[HomeDs], None] = do_nothing,
                 pre_sds_return_value: Optional[TextRenderer] = None,
                 post_setup_action: Callable[[TestCaseDs], None] = do_nothing,
                 post_setup_return_value: Optional[TextRenderer] = None,
                 ):
        self.post_setup_return_value = post_setup_return_value
        self.pre_sds_return_value = pre_sds_return_value
        self.post_setup_action = post_setup_action
        self.pre_sds_action = pre_sds_action

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        self.pre_sds_action(hds)
        return self.pre_sds_return_value

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        self.post_setup_action(tcds)
        return self.post_setup_return_value

    @staticmethod
    def corresponding_to(result: ValidationActual) -> DdvValidator:
        return DdvValidatorThat(
            pre_sds_return_value=asrt_text_doc.new_single_string_text_for_test__optional(result.pre_sds),
            post_setup_return_value=asrt_text_doc.new_single_string_text_for_test__optional(result.post_sds),
        )


def constant(result: ValidationActual) -> DdvValidator:
    return DdvValidatorThat(
        pre_sds_return_value=asrt_text_doc.new_single_string_text_for_test__optional(result.pre_sds),
        post_setup_return_value=asrt_text_doc.new_single_string_text_for_test__optional(result.post_sds),
    )
