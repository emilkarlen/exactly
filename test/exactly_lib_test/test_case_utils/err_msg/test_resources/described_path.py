from pathlib import Path

from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.err_msg2.path_impl.described_path_w_handler import DescribedPathPrimitiveWHandler
from exactly_lib_test.test_case_utils.err_msg.test_resources.path_describer import \
    PathDescriberHandlerForPrimitiveTestImpl


def new_primitive(path: Path) -> DescribedPathPrimitive:
    return DescribedPathPrimitiveWHandler(
        path,
        PathDescriberHandlerForPrimitiveTestImpl(str(path))
    )
