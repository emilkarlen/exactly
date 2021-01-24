from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib_test.test_resources.actions import do_nothing


class SdvValidatorThat(SdvValidator):
    def __init__(self,
                 pre_sds_action=do_nothing,
                 pre_sds_return_value: Optional[TextRenderer] = None,
                 post_setup_action=do_nothing,
                 post_setup_return_value: Optional[TextRenderer] = None,
                 ):
        self.post_setup_return_value = post_setup_return_value
        self.pre_sds_return_value = pre_sds_return_value
        self.post_setup_action = post_setup_action
        self.pre_sds_action = pre_sds_action

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        self.pre_sds_action(environment)
        return self.pre_sds_return_value

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        self.post_setup_action(environment)
        return self.post_setup_return_value
