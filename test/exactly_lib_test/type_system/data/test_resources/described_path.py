from pathlib import Path

from exactly_lib.type_system.data.impl.path.described_w_handler import DescribedPathWHandler
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib_test.type_system.data.test_resources.path_describer import \
    PathDescriberHandlerForPrimitiveTestImpl


def new_primitive(path: Path) -> DescribedPath:
    return DescribedPathWHandler(
        path,
        PathDescriberHandlerForPrimitiveTestImpl(str(path))
    )
