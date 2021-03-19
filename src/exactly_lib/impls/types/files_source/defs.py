import enum

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path import path_relativities
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionArgumentConfiguration


class ModificationType(enum.Enum):
    CREATE = 1
    APPEND = 2


class FileType(enum.Enum):
    REGULAR = 1
    DIR = 2


def src_dir_path_argument(argument_syntax_name: str) -> RelOptionArgumentConfiguration:
    return path_relativities.argument_config__read(
        argument_syntax_name,
        phase_is_after_act=False,
        default=RelOptionType.REL_HDS_CASE,
    )
