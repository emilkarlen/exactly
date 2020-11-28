import unittest

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_deps.types.string_model.ddv import StringModelDdv
from exactly_lib.type_val_deps.types.string_model.sdv import StringModelSdv
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.common_properties_checker import \
    CommonPropertiesConfiguration, Applier, CommonSdvPropertiesChecker, ApplierThatDoesNothing
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.sdv_checker import \
    WithNodeDescriptionExecutionPropertiesChecker


class StringModelPropertiesConfiguration(
    CommonPropertiesConfiguration[StringModel,
                                  None,
                                  None]):
    def __init__(self):
        self._applier = ApplierThatDoesNothing()

    def applier(self) -> Applier[StringModel, None, None]:
        return self._applier

    def new_sdv_checker(self) -> CommonSdvPropertiesChecker[StringModel]:
        return _SdvPropertiesChecker()

    def new_execution_checker(self) -> WithNodeDescriptionExecutionPropertiesChecker[None]:
        return WithNodeDescriptionExecutionPropertiesChecker(
            StringModelDdv,
            StringModel,
            asrt.anything_goes(),
        )


class _SdvPropertiesChecker(CommonSdvPropertiesChecker[StringModel]):
    def check(self,
              put: unittest.TestCase,
              actual: FullDepsSdv[StringModel],
              message_builder: MessageBuilder,
              ):
        asrt.is_instance(StringModelSdv).apply(
            put,
            actual,
            message_builder
        )
