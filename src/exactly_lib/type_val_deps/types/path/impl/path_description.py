import pathlib
from typing import Optional

from exactly_lib.tcfs import path_relativity as pr
from exactly_lib.tcfs import relative_path_options as rpo
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv

EXACTLY_SANDBOX_ROOT_DIR_NAME = 'EXACTLY_SANDBOX'


def _with_prefix(prefix: str, path_ddv: PathDdv) -> str:
    return str(pathlib.PurePosixPath(prefix, path_ddv.path_suffix().value()))


def path_ddv_with_relativity_name_prefix__rel_tcds_dir(path_ddv: PathDdv) -> str:
    relativity_type = path_ddv.relativity().relativity_type

    if relativity_type is None:
        raise ValueError('path is absolute')

    if relativity_type is RelOptionType.REL_CWD:
        raise ValueError('path is relative ' + str(RelOptionType.REL_CWD))

    rel_hds_opt = pr.rel_hds_from_rel_any(relativity_type)
    if rel_hds_opt is not None:
        return _with_prefix(rpo.REL_HDS_OPTIONS_MAP[rel_hds_opt].directory_symbol_reference,
                            path_ddv)

    rel_sds_opt = pr.rel_sds_from_rel_any(relativity_type)
    if rel_sds_opt is not None:
        return _with_prefix(rpo.REL_SDS_OPTIONS_MAP[rel_sds_opt].directory_symbol_reference,
                            path_ddv)

    raise ValueError(
        'undefined relativity of {}: {}: '.format(path_ddv, relativity_type)
    )


def path_ddv_with_relativity_name_prefix(path_ddv: PathDdv,
                                         tcds: TestCaseDs,
                                         cwd: Optional[pathlib.Path]) -> str:
    def absolute() -> str:
        return str(path_ddv.value_when_no_dir_dependencies())

    def rel_cwd() -> str:
        def value_if_cwd_is_relative_root_dir(rel_root_dir_path: pathlib.Path,
                                              rel_dir_name: str) -> str:
            cwd_rel_to_option_root = cwd.relative_to(rel_root_dir_path)
            return str(pathlib.PurePosixPath(rel_dir_name,
                                             cwd_rel_to_option_root,
                                             path_ddv.path_suffix().value()))

        for rel_sds_option_info in rpo.REL_SDS_OPTIONS_MAP.values():
            try:
                return value_if_cwd_is_relative_root_dir(
                    rel_sds_option_info.root_resolver.from_tcds(tcds),
                    rel_sds_option_info.directory_symbol_reference)
            except ValueError:
                continue

        for rel_hds_option_info in rpo.REL_HDS_OPTIONS_MAP.values():
            try:
                return value_if_cwd_is_relative_root_dir(
                    rel_hds_option_info.root_resolver.from_tcds(tcds),
                    rel_hds_option_info.directory_symbol_reference)
            except ValueError:
                continue

        try:
            return value_if_cwd_is_relative_root_dir(
                tcds.sds.root_dir,
                EXACTLY_SANDBOX_ROOT_DIR_NAME)
        except ValueError:
            return str(path_ddv.value_of_any_dependency(tcds))

    relativity = path_ddv.relativity()

    if relativity.is_absolute:
        return absolute()

    relativity_type = relativity.relativity_type

    if relativity_type is pr.RelOptionType.REL_CWD:
        return rel_cwd()

    return path_ddv_with_relativity_name_prefix__rel_tcds_dir(path_ddv)
