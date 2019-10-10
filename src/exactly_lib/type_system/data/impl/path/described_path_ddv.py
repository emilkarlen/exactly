from exactly_lib.type_system.data.described_path import DescribedPathValue
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.impl.path import described_w_handler
from exactly_lib.type_system.data.impl.path import describer_handlers


def new__with_cwd_as_cd(path: FileRef) -> DescribedPathValue:
    return described_w_handler.DescribedPathValueWHandler(
        path,
        describer_handlers.PathDescriberHandlerForValueWithValue(path, True),
    )


def new__with_unknown_cd(path: FileRef) -> DescribedPathValue:
    return described_w_handler.DescribedPathValueWHandler(
        path,
        describer_handlers.PathDescriberHandlerForValueWithValue(path, False),
    )
