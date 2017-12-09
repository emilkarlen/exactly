import pathlib

from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure import path_relativity as pr
from exactly_lib.test_case_file_structure import relative_path_options as rpo
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessagePartConstructor
from exactly_lib.type_system.data.file_ref import FileRef

EXACTLY_SANDBOX_ROOT_DIR_NAME = 'EXACTLY_SANDBOX'


class PathValuePartConstructor(ErrorMessagePartConstructor):
    def __init__(self, path_resolver: FileRefResolver):
        self.path_resolver = path_resolver

    def lines(self, environment: InstructionEnvironmentForPostSdsStep) -> list:
        path_resolve_env = environment.path_resolving_environment_pre_or_post_sds
        path_value = self.path_resolver.resolve(path_resolve_env.symbols)

        return lines_for_path_value(path_value, environment.home_and_sds)


def lines_for_path_value(path_value: FileRef, tcds: HomeAndSds) -> list:
    the_cwd = pathlib.Path.cwd()

    presentation_str = path_value_with_relativity_name_prefix(path_value,
                                                              tcds,
                                                              the_cwd)

    ret_val = [presentation_str]

    def path_is_rel_home() -> bool:
        if path_value.relativity().is_relative:
            relativity_type = path_value.relativity().relativity_type
            return pr.rel_home_from_rel_any(relativity_type) is not None
        else:
            return False

    if path_is_rel_home():
        abs_path_str = str(path_value.value_of_any_dependency(tcds))
        ret_val.append(abs_path_str)
    return ret_val


def path_value_with_relativity_name_prefix(path_value: FileRef,
                                           home_and_sds: HomeAndSds,
                                           cwd: pathlib.Path) -> str:
    def with_prefix(prefix: str) -> str:
        return str(pathlib.PurePosixPath(prefix, path_value.path_suffix().value()))

    def rel_home(relativity: rpo.RelHomeOptionType) -> str:
        return with_prefix(rpo.REL_HOME_OPTIONS_MAP[relativity].directory_variable_name)

    def rel_sds(relativity: pr.RelSdsOptionType) -> str:
        return with_prefix(rpo.REL_SDS_OPTIONS_MAP[relativity].directory_variable_name)

    def absolute() -> str:
        return str(path_value.value_of_any_dependency(home_and_sds))

    def rel_cwd() -> str:
        def value_if_cwd_is_relative_root_dir(rel_root_dir_path: pathlib.Path,
                                              rel_dir_name: str) -> str:
            cwd_rel_to_option_root = cwd.relative_to(rel_root_dir_path)
            return str(pathlib.PurePosixPath(rel_dir_name,
                                             cwd_rel_to_option_root,
                                             path_value.path_suffix().value()))

        for rel_sds_option_info in rpo.REL_SDS_OPTIONS_MAP.values():
            try:
                return value_if_cwd_is_relative_root_dir(
                    rel_sds_option_info.root_resolver.from_home_and_sds(home_and_sds),
                    rel_sds_option_info.directory_variable_name)
            except ValueError:
                continue

        for rel_home_option_info in rpo.REL_HOME_OPTIONS_MAP.values():
            try:
                return value_if_cwd_is_relative_root_dir(
                    rel_home_option_info.root_resolver.from_home_and_sds(home_and_sds),
                    rel_home_option_info.directory_variable_name)
            except ValueError:
                continue

        try:
            return value_if_cwd_is_relative_root_dir(
                home_and_sds.sds.root_dir,
                EXACTLY_SANDBOX_ROOT_DIR_NAME)
        except ValueError:
            return str(path_value.value_of_any_dependency(home_and_sds))

    relativity = path_value.relativity()

    if relativity.is_absolute:
        return absolute()

    relativity_type = relativity.relativity_type

    if relativity_type is pr.RelOptionType.REL_CWD:
        return rel_cwd()

    rel_home_opt = pr.rel_home_from_rel_any(relativity_type)
    if rel_home_opt is not None:
        return rel_home(rel_home_opt)

    rel_sds_opt = pr.rel_sds_from_rel_any(relativity_type)
    if rel_sds_opt is not None:
        return rel_sds(rel_sds_opt)

    path_lib_path = path_value.value_of_any_dependency(home_and_sds)
    err_msg = 'Unknown relativity: {}\nOf path {}'.format(str(relativity_type),
                                                          str(path_lib_path))
    raise ValueError(err_msg)


def path_value_description(property_name: str,
                           path_resolver: FileRefResolver) -> property_description.PropertyDescriptor:
    return property_description.PropertyDescriptorWithConstantPropertyName(
        property_name,
        PathValuePartConstructor(path_resolver),
    )
