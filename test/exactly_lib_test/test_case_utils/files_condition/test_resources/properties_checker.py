import unittest

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.test_case_utils.files_condition.structure import FilesCondition, FilesConditionSdv, \
    FilesConditionDdv
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier, CommonSdvPropertiesChecker
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import \
    WithDetailsDescriptionExecutionPropertiesChecker
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


class FilesConditionPropertiesConfiguration(
    CommonPropertiesConfiguration[FilesCondition,
                                  None,
                                  None]):
    def __init__(self):
        self._applier = _UnusedApplier()

    def applier(self) -> Applier[FilesCondition, None, None]:
        return self._applier

    def new_sdv_checker(self) -> CommonSdvPropertiesChecker[FilesCondition]:
        return _SdvPropertiesChecker()

    def new_execution_checker(self) -> WithDetailsDescriptionExecutionPropertiesChecker:
        return WithDetailsDescriptionExecutionPropertiesChecker(FilesConditionDdv, FilesCondition)


class _SdvPropertiesChecker(CommonSdvPropertiesChecker[FilesCondition]):
    def check(self,
              put: unittest.TestCase,
              actual: LogicSdv[FilesCondition],
              message_builder: MessageBuilder,
              ):
        asrt.is_instance(FilesConditionSdv).apply(
            put,
            actual,
            message_builder
        )


class _UnusedApplier(Applier[FilesCondition, None, None]):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: FilesCondition,
              resolving_environment: FullResolvingEnvironment,
              input_: None) -> None:
        return None
