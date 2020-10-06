import unittest

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import LogicSdvPropertiesChecker, \
    WithTreeStructureExecutionPropertiesChecker
from exactly_lib_test.test_case_utils.string_models.test_resources.model_constructor import ModelConstructor
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_system.logic.string_model.test_resources import assertions as asrt_string_model


class StringTransformerPropertiesConfiguration(
    CommonPropertiesConfiguration[StringTransformer,
                                  ModelConstructor,
                                  StringModel]):
    def __init__(self):
        self._applier = _Applier()

    def applier(self) -> Applier[StringTransformer, ModelConstructor, StringModel]:
        return self._applier

    def new_sdv_checker(self) -> LogicSdvPropertiesChecker[StringTransformer]:
        return LogicSdvPropertiesChecker(StringTransformerSdv)

    def new_execution_checker(self) -> WithTreeStructureExecutionPropertiesChecker[StringModel]:
        return WithTreeStructureExecutionPropertiesChecker(
            StringTransformerDdv,
            StringTransformer,
            asrt_string_model.StringModelLinesAreValidAssertion(),
        )


class _Applier(Applier[StringTransformer, ModelConstructor, StringModel]):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: StringTransformer,
              resolving_environment: FullResolvingEnvironment,
              input_: ModelConstructor) -> StringModel:
        model = primitive.transform(input_(resolving_environment))
        self._force_evaluation_of_model(model)
        return model

    @staticmethod
    def _force_evaluation_of_model(model: StringModel):
        with model.as_lines:
            pass
