from exactly_lib.impls import file_properties
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.path import path_check
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import PRIMITIVE
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.string.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_model.ddv import StringModelDdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib.type_val_prims.string_model.structure_builder import StringModelStructureBuilder
from . import constant_str, file_model
from ...file_properties import FileType


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
        self._validator = path_check.PathCheckDdvValidator(
            path_check.PathCheckDdv(
                path,
                file_properties.must_exist_as(FileType.REGULAR)
            )
        )

    def new_structure_builder(self) -> StringModelStructureBuilder:
        return file_model.StringModelOfFile.structure_builder_for(
            custom_details.PathDdvDetailsRenderer(self._path.describer())
        )

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        def make_primitive(environment: ApplicationEnvironment) -> StringModel:
            return file_model.string_model_of_file__described(
                self._path.value_of_any_dependency__d(tcds),
                environment.tmp_files_space,
            )

        return advs.AdvFromFunction(make_primitive)


class TransformedStringModelDdv(StringModelDdv):
    def __init__(self,
                 transformed: StringModelDdv,
                 transformer: StringTransformerDdv,
                 ):
        self._transformed = transformed
        self._transformer = transformer

    def new_structure_builder(self) -> StringModelStructureBuilder:
        return self._transformed.new_structure_builder().with_transformed_by(self._transformer.structure())

    @property
    def validator(self) -> DdvValidator:
        return ddv_validators.all_of([self._transformed.validator,
                                      self._transformer.validator])

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        def make_primitive(environment: ApplicationEnvironment) -> StringModel:
            transformed = self._transformed.value_of_any_dependency(tcds).primitive(environment)
            transformer = self._transformer.value_of_any_dependency(tcds).primitive(environment)
            return transformer.transform(transformed)

        return advs.AdvFromFunction(make_primitive)
