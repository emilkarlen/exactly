from exactly_lib.impls.description_tree import custom_details
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import PRIMITIVE
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.string.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_model.ddv import StringModelDdv
from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib.type_val_prims.string_model.structure_builder import StringModelStructureBuilder
from . import constant_str, file_model


class ConstantStringStringModelDdv(StringModelDdv):
    def __init__(self, string: StringDdv):
        self._string = string

    def new_structure_builder(self) -> StringModelStructureBuilder:
        return constant_str.StringModel.structure_builder_for(self._string.describer())

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        def make_primitive(environment: ApplicationEnvironment) -> StringModel:
            return constant_str.StringModel(
                self._string.value_of_any_dependency(tcds),
                environment.tmp_files_space,
            )

        return advs.AdvFromFunction(make_primitive)


class PathStringModelDdv(StringModelDdv):
    def __init__(self, path: PathDdv):
        self._path = path

    def new_structure_builder(self) -> StringModelStructureBuilder:
        return file_model.StringModelOfFile.structure_builder_for(
            custom_details.PathDdvDetailsRenderer(self._path.describer())
        )

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        def make_primitive(environment: ApplicationEnvironment) -> StringModel:
            return file_model.string_model_of_file__described(
                self._path.value_of_any_dependency__d(tcds),
                environment.tmp_files_space,
            )

        return advs.AdvFromFunction(make_primitive)
