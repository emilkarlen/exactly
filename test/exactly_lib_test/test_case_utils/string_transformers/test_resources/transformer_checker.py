import unittest
from typing import Callable

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv
from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, Applier
from exactly_lib_test.test_case_utils.logic.test_resources.logic_type_checker import LogicSdvPropertiesChecker, \
    WithTreeStructureExecutionPropertiesChecker
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder

ModelConstructor = Callable[[TmpDirFileSpace], StringModel]


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

    def new_execution_checker(self) -> WithTreeStructureExecutionPropertiesChecker:
        return WithTreeStructureExecutionPropertiesChecker(StringTransformerDdv, StringTransformer)


class _Applier(Applier[StringTransformer, ModelConstructor, StringModel]):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: StringTransformer,
              resolving_environment: FullResolvingEnvironment,
              input_: ModelConstructor) -> StringModel:
        return primitive.transform(input_(resolving_environment.application_environment.tmp_files_space))
