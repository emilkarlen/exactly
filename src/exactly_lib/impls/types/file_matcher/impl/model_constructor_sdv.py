from typing import Callable

from exactly_lib.common import tmp_dir_file_spaces
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue, \
    ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps import w_details_impls as ddv_w_details_impls
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithDetailsDescriptionDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps import w_details_impls
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsWithDetailsDescriptionSdv
from exactly_lib.util.symbol_table import SymbolTable
from .model_constructor import ModelConstructor, MODEL
from ...string_source.factory import RootStringSourceFactory


def with_string_source_construction(make_constructor: Callable[[RootStringSourceFactory], ModelConstructor[MODEL]],
                                    ) -> FullDepsWithDetailsDescriptionSdv[ModelConstructor[MODEL]]:
    def make_primitive(environment: ApplicationEnvironment) -> ModelConstructor[MODEL]:
        factory = RootStringSourceFactory(
            tmp_dir_file_spaces.std_tmp_dir_file_space(environment.tmp_files_space.new_path())
        )
        return make_constructor(factory)

    def make_adv(tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[ModelConstructor[MODEL]]:
        return advs.AdvFromFunction(make_primitive)

    def make_ddv(symbols: SymbolTable) -> FullDepsWithDetailsDescriptionDdv[ModelConstructor[MODEL]]:
        return ddv_w_details_impls.DdvFromParts(make_adv)

    return w_details_impls.SdvFromParts(make_ddv)
