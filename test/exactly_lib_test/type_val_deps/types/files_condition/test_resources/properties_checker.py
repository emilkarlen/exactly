import unittest

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_deps.types.files_condition.sdv import FilesCondition, FilesConditionSdv, \
    FilesConditionDdv
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier, CommonSdvPropertiesChecker, ApplierThatDoesNothing
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources.sdv_checker import \
    WithDetailsDescriptionExecutionPropertiesChecker


class FilesConditionPropertiesConfiguration(
    CommonPropertiesConfiguration[FilesCondition,
                                  None,
                                  None]):
    def __init__(self):
        self._applier = ApplierThatDoesNothing()

    def applier(self) -> Applier[FilesCondition, None, None]:
        return self._applier

    def new_sdv_checker(self) -> CommonSdvPropertiesChecker[FilesCondition]:
        return _SdvPropertiesChecker()

    def new_execution_checker(self) -> WithDetailsDescriptionExecutionPropertiesChecker[FilesCondition, None]:
        return WithDetailsDescriptionExecutionPropertiesChecker(
            FilesConditionDdv,
            FilesCondition, asrt.anything_goes(),
        )


class _SdvPropertiesChecker(CommonSdvPropertiesChecker[FilesCondition]):
    def check(self,
              put: unittest.TestCase,
              actual: FullDepsSdv[FilesCondition],
              message_builder: MessageBuilder,
              ):
        asrt.is_instance(FilesConditionSdv).apply(
            put,
            actual,
            message_builder
        )
