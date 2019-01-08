from typing import Optional, Callable

from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration


class Model:
    def __init__(self,
                 dir_path_resolver: FileRefResolver,
                 files_selection: Optional[FileMatcherResolver] = None
                 ):
        self.dir_path_resolver = dir_path_resolver
        self.files_selection = files_selection


ModelConstructorFromRelOptConf = Callable[[RelativityOptionConfiguration], Model]


def model_with_rel_root_as_source_path(root_dir_of_dir_contents: RelativityOptionConfiguration) -> Model:
    return Model(root_dir_of_dir_contents.file_ref_resolver_for())


def model_with_source_path_as_sub_dir_of_rel_root(subdir: str) -> ModelConstructorFromRelOptConf:
    def ret_val(root_dir_of_dir_contents: RelativityOptionConfiguration) -> Model:
        return Model(root_dir_of_dir_contents.file_ref_resolver_for(subdir))

    return ret_val


def arbitrary_model() -> Model:
    return Model(
        file_ref_resolvers.of_rel_option(RelOptionType.REL_ACT),
        None)
