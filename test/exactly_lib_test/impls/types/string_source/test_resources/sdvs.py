from exactly_lib.impls.types.string_source.sdvs import ConstantStringStringSourceSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv


def const_str(contents: str) -> StringSourceSdv:
    return ConstantStringStringSourceSdv(string_sdvs.str_constant(contents))
