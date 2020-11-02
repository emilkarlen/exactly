import unittest

from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib_test.impls.types.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier
from exactly_lib_test.impls.types.logic.test_resources.logic_type_checker import LogicSdvPropertiesChecker, \
    WithTreeStructureExecutionPropertiesChecker
from exactly_lib_test.impls.types.string_models.test_resources.model_constructor import ModelConstructor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_prims.string_model.test_resources import assertions as asrt_string_model


class StringTransformerPropertiesConfiguration(
    CommonPropertiesConfiguration[StringTransformer,
                                  ModelConstructor,
                                  StringModel]):
    def __init__(self, avoid_model_evaluation: bool):
        self._avoid_model_evaluation = avoid_model_evaluation
        self._applier = _Applier(not avoid_model_evaluation)

    def applier(self) -> Applier[StringTransformer, ModelConstructor, StringModel]:
        return self._applier

    def new_sdv_checker(self) -> LogicSdvPropertiesChecker[StringTransformer]:
        return LogicSdvPropertiesChecker(StringTransformerSdv)

    def new_execution_checker(self) -> WithTreeStructureExecutionPropertiesChecker[StringModel]:
        generic_model_check = (
            asrt.anything_goes()
            if self._avoid_model_evaluation
            else
            asrt_string_model.StringModelLinesAreValidAssertion()
        )
        return WithTreeStructureExecutionPropertiesChecker(
            StringTransformerDdv,
            StringTransformer,
            generic_model_check,
        )


class _Applier(Applier[StringTransformer, ModelConstructor, StringModel]):
    def __init__(self, force_evaluation_of_model: bool):
        self._force_evaluation_of_model = force_evaluation_of_model

    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: StringTransformer,
              resolving_environment: FullResolvingEnvironment,
              input_: ModelConstructor) -> StringModel:
        model = primitive.transform(input_(resolving_environment))
        self._mb_force_evaluation_of_model(model)
        return model

    def _mb_force_evaluation_of_model(self, model: StringModel):
        if self._force_evaluation_of_model:
            with model.as_lines:
                pass
