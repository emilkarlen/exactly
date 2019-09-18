from pathlib import Path

from exactly_lib.symbol.data.impl.path.described_w_handler import DescribedPathPrimitiveWHandler
from exactly_lib.type_system.data.described_path import DescribedPathPrimitive
from exactly_lib_test.test_case_utils.err_msg.test_resources.path_describer import \
    PathDescriberHandlerForPrimitiveTestImpl


def new_primitive(path: Path) -> DescribedPathPrimitive:
    return DescribedPathPrimitiveWHandler(
        path,
        PathDescriberHandlerForPrimitiveTestImpl(str(path))
    )
