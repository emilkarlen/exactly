from typing import Callable

from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.described_dep_val import LogicWithDescriberSdv, LogicWithDetailsDescriptionDdv
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand
from exactly_lib.util.symbol_table import SymbolTable
from .model_constructor import ModelConstructor, MODEL
from ... import described_dep_val
from ...string_models.factory import StringModelFactory


def with_string_model_construction(make_constructor: Callable[[StringModelFactory], ModelConstructor[MODEL]],
                                   ) -> LogicWithDescriberSdv[ModelConstructor[MODEL]]:
    def make_primitive(environment: ApplicationEnvironment) -> ModelConstructor[MODEL]:
        factory = StringModelFactory(
            TmpDirFileSpaceAsDirCreatedOnDemand(environment.tmp_files_space.new_path())
        )
        return make_constructor(factory)

    def make_adv(tcds: Tcds) -> ApplicationEnvironmentDependentValue[ModelConstructor[MODEL]]:
        return advs.AdvFromFunction(make_primitive)

    def make_ddv(symbols: SymbolTable) -> LogicWithDetailsDescriptionDdv[ModelConstructor[MODEL]]:
        return described_dep_val.DdvFromParts(make_adv)

    return described_dep_val.SdvFromParts(make_ddv)
