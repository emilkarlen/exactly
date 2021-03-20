import unittest

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib_test.impls.types.string_source.test_resources.model_constructor import ModelConstructor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources.sdv_checker import \
    FullDepsSdvPropertiesChecker, \
    WithNodeDescriptionExecutionPropertiesChecker
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source


class StringTransformerPropertiesConfiguration(
    CommonPropertiesConfiguration[StringTransformer,
                                  ModelConstructor,
                                  StringSource]):
    def __init__(self, avoid_model_evaluation: bool):
        self._avoid_model_evaluation = avoid_model_evaluation
        self._applier = _Applier(not avoid_model_evaluation)

    def applier(self) -> Applier[StringTransformer, ModelConstructor, StringSource]:
        return self._applier

    def new_sdv_checker(self) -> FullDepsSdvPropertiesChecker[StringTransformer]:
        return FullDepsSdvPropertiesChecker(StringTransformerSdv)

    def new_execution_checker(self) -> WithNodeDescriptionExecutionPropertiesChecker[StringTransformer, StringSource]:
        generic_model_check = (
            asrt.anything_goes()
            if self._avoid_model_evaluation
            else
            asrt_string_source.StringSourceLinesAreValidAssertion()
        )
        return WithNodeDescriptionExecutionPropertiesChecker(
            StringTransformerDdv,
            StringTransformer,
            generic_model_check,
        )


class _Applier(Applier[StringTransformer, ModelConstructor, StringSource]):
    def __init__(self, force_evaluation_of_model: bool):
        self._force_evaluation_of_model = force_evaluation_of_model

    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: StringTransformer,
              resolving_environment: FullResolvingEnvironment,
              input_: ModelConstructor) -> StringSource:
        model = primitive.transform(input_(resolving_environment))
        self._mb_force_evaluation_of_model(model)
        return model

    def _mb_force_evaluation_of_model(self, model: StringSource):
        if self._force_evaluation_of_model:
            with model.contents().as_lines:
                pass
