from typing import Optional, Callable

from exactly_lib.impls.types.files_matcher import models
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.dep_variants.sdv.resolving_helper import resolving_helper__of_full_env
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherSdv
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration


class ModelEmbryo:
    def __init__(self,
                 dir_path_sdv: PathSdv,
                 files_selection: Optional[FileMatcherSdv] = None
                 ):
        self.dir_path_sdv = dir_path_sdv
        self.files_selection = files_selection


ModelConstructor = Callable[[FullResolvingEnvironment], FilesMatcherModel]

ModelConstructorFromRelOptConf = Callable[[RelativityOptionConfiguration], ModelConstructor]


def model_with_rel_root_as_source_path(root_dir_of_dir_contents: RelativityOptionConfiguration) -> ModelConstructor:
    return model_constructor__from_embryo__non_recursive(ModelEmbryo(root_dir_of_dir_contents.path_sdv_for()))


def model_with_source_path_as_sub_dir_of_rel_root(subdir: str) -> ModelConstructorFromRelOptConf:
    def ret_val(root_dir_of_dir_contents: RelativityOptionConfiguration) -> ModelConstructor:
        return model_constructor__from_embryo__non_recursive(ModelEmbryo(root_dir_of_dir_contents.path_sdv_for(subdir)))

    return ret_val


def arbitrary_model_constructor() -> ModelConstructorFromRelOptConf:
    def ret_val(root_dir_of_dir_contents: RelativityOptionConfiguration) -> ModelConstructor:
        return arbitrary_model()

    return ret_val


def arbitrary_model() -> ModelConstructor:
    return model_constructor__from_embryo__non_recursive(ModelEmbryo(
        path_sdvs.of_rel_option(RelOptionType.REL_ACT),
        None))


def model_constructor__from_embryo__non_recursive(embryo: ModelEmbryo) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FilesMatcherModel:
        fs = embryo.files_selection
        resolved_path = (
            embryo.dir_path_sdv
                .resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )
        resolved_selection = (
            None
            if fs is None
            else resolving_helper__of_full_env(environment).resolve_matcher(fs)
        )

        model = models.non_recursive(resolved_path)
        if resolved_selection is not None:
            model = model.sub_set(resolved_selection)

        return model

    return ret_val


def model_constructor__recursive(checked_dir: PathSdv,
                                 min_depth: Optional[int] = None,
                                 max_depth: Optional[int] = None,
                                 ) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FilesMatcherModel:
        checked_dir_path = (
            checked_dir
                .resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )

        return models.recursive(checked_dir_path,
                                min_depth,
                                max_depth)

    return ret_val


def model_constructor__non_recursive(checked_dir: PathSdv) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> FilesMatcherModel:
        checked_dir_path = (
            checked_dir
                .resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )

        return models.non_recursive(checked_dir_path)

    return ret_val
