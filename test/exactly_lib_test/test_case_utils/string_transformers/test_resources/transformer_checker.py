import unittest
from typing import Callable

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel, \
    StringTransformerDdv
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import LogicSdvPropertiesChecker, \
    WithTreeStructureExecutionPropertiesChecker
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder

ModelConstructor = Callable[[], StringTransformerModel]


class StringTransformerPropertiesConfiguration(
    CommonPropertiesConfiguration[StringTransformer,
                                  ModelConstructor,
                                  StringTransformerModel]):
    def __init__(self):
        self._applier = _Applier()

    def applier(self) -> Applier[StringTransformer, ModelConstructor, StringTransformerModel]:
        return self._applier

    def new_sdv_checker(self) -> LogicSdvPropertiesChecker[StringTransformer]:
        return LogicSdvPropertiesChecker(StringTransformerSdv)

    def new_execution_checker(self) -> WithTreeStructureExecutionPropertiesChecker:
        return WithTreeStructureExecutionPropertiesChecker(StringTransformerDdv, StringTransformer)


class _Applier(Applier[StringTransformer, ModelConstructor, StringTransformerModel]):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: StringTransformer,
              resolving_environment: FullResolvingEnvironment,
              input_: ModelConstructor) -> StringTransformerModel:
        return primitive.transform(input_())
