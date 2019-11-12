from pathlib import Path

from exactly_lib.type_system.data.impl.path.described_w_handler import DescribedPathPrimitiveWHandler
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib_test.type_system.data.test_resources.path_describer import \
    PathDescriberHandlerForPrimitiveTestImpl


def new_primitive(path: Path) -> DescribedPathPrimitive:
    return DescribedPathPrimitiveWHandler(
        path,
        PathDescriberHandlerForPrimitiveTestImpl(str(path))
    )
