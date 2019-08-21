from pathlib import Path

from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.err_msg2.path_impl.described_path_w_handler import DescribedPathPrimitiveImpl
from exactly_lib_test.test_case_utils.err_msg.test_resources.path_describer import PathDescriberForPrimitiveTestImpl


def new_primitive(path: Path) -> DescribedPathPrimitive:
    return DescribedPathPrimitiveImpl(
        path,
        PathDescriberForPrimitiveTestImpl(str(path))
    )
