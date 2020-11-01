from pathlib import Path

from exactly_lib.type_val_deps.types.path.impl.described_w_handler import DescribedPathWHandler
from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib_test.type_val_deps.types.path.test_resources.path_describer import \
    PathDescriberHandlerForPrimitiveTestImpl


def new_primitive(path: Path) -> DescribedPath:
    return DescribedPathWHandler(
        path,
        PathDescriberHandlerForPrimitiveTestImpl(str(path))
    )
