from pathlib import Path
from typing import Optional

from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.type_val_prims.path_describer import PathDescriberForPrimitive
from .impl import describer_from_str, primitive_str_renderers


def poor_describer(path: Path) -> PathDescriberForPrimitive:
    """
    Gives a describer, which poor, since it describes the
    path as an absolute path with no dir-dependencies.

    The reason for the poorness is that the TCDS is unknown.
    """
    str_renderer = primitive_str_renderers.Constant(path)
    return describer_from_str.PathDescriberForPrimitiveFromStr(
        describer_from_str.PathDescriberForDdvFromStr(
            str_renderer,
            _no_deps_since_unknown,
        ),
        str_renderer,
    )


def _no_deps_since_unknown() -> Optional[DirectoryStructurePartition]:
    return None
