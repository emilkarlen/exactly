from typing import Callable

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerModel, \
    StringTransformerDdv
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import LogicTypeSdvPropertiesChecker, \
    WithTreeStructureExecutionPropertiesChecker

ModelConstructor = Callable[[], StringTransformerModel]


class StringTransformerPropertiesConfiguration(
    CommonPropertiesConfiguration[StringTransformer,
                                  ModelConstructor,
                                  StringTransformerModel]):

    def apply(self,
              primitive: StringTransformer,
              resolving_environment: FullResolvingEnvironment,
              input_: ModelConstructor) -> StringTransformerModel:
        return primitive.transform(input_())

    def new_sdv_checker(self) -> LogicTypeSdvPropertiesChecker[StringTransformer]:
        return LogicTypeSdvPropertiesChecker(LogicValueType.STRING_TRANSFORMER,
                                             StringTransformerSdv)

    def new_execution_checker(self) -> WithTreeStructureExecutionPropertiesChecker:
        return WithTreeStructureExecutionPropertiesChecker(StringTransformerDdv, StringTransformer)
