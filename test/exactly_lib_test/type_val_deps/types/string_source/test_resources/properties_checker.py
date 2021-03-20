import unittest

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier, CommonSdvPropertiesChecker, ApplierThatDoesNothing
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources.sdv_checker import \
    WithNodeDescriptionExecutionPropertiesChecker


class StringSourcePropertiesConfiguration(
    CommonPropertiesConfiguration[StringSource,
                                  None,
                                  None]):
    def __init__(self):
        self._applier = ApplierThatDoesNothing()

    def applier(self) -> Applier[StringSource, None, None]:
        return self._applier

    def new_sdv_checker(self) -> CommonSdvPropertiesChecker[StringSource]:
        return _SdvPropertiesChecker()

    def new_execution_checker(self) -> WithNodeDescriptionExecutionPropertiesChecker[StringSource, None]:
        return WithNodeDescriptionExecutionPropertiesChecker(
            StringSourceDdv,
            StringSource,
            asrt.anything_goes(),
        )


class _SdvPropertiesChecker(CommonSdvPropertiesChecker[StringSource]):
    def check(self,
              put: unittest.TestCase,
              actual: FullDepsSdv[StringSource],
              message_builder: MessageBuilder,
              ):
        asrt.is_instance(StringSourceSdv).apply(
            put,
            actual,
            message_builder
        )
