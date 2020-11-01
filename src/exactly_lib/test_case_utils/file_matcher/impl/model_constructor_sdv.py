from typing import Callable

from exactly_lib.common import tmp_dir_file_spaces
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case_utils.described_dep_val import LogicWithDetailsDescriptionSdv, LogicWithDetailsDescriptionDdv
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue, \
    ApplicationEnvironment
from exactly_lib.util.symbol_table import SymbolTable
from .model_constructor import ModelConstructor, MODEL
from ... import described_dep_val
from ...string_models.factory import RootStringModelFactory


def with_string_model_construction(make_constructor: Callable[[RootStringModelFactory], ModelConstructor[MODEL]],
                                   ) -> LogicWithDetailsDescriptionSdv[ModelConstructor[MODEL]]:
    def make_primitive(environment: ApplicationEnvironment) -> ModelConstructor[MODEL]:
        factory = RootStringModelFactory(
            tmp_dir_file_spaces.std_tmp_dir_file_space(environment.tmp_files_space.new_path())
        )
        return make_constructor(factory)

    def make_adv(tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[ModelConstructor[MODEL]]:
        return advs.AdvFromFunction(make_primitive)

    def make_ddv(symbols: SymbolTable) -> LogicWithDetailsDescriptionDdv[ModelConstructor[MODEL]]:
        return described_dep_val.DdvFromParts(make_adv)

    return described_dep_val.SdvFromParts(make_ddv)
