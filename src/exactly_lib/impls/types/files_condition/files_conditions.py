from typing import Sequence, Tuple, Optional

from exactly_lib.impls.types.files_condition.impl import constant, reference
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherSdv
from exactly_lib.type_val_deps.types.files_condition.sdv import FilesConditionSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv


def new_constant(files: Sequence[Tuple[StringSdv, Optional[FileMatcherSdv]]]) -> FilesConditionSdv:
    return constant.ConstantSdv(files)


def new_empty() -> FilesConditionSdv:
    return constant.ConstantSdv(())


def new_reference(symbol_name: str) -> FilesConditionSdv:
    return reference.ReferenceSdv(symbol_name)
