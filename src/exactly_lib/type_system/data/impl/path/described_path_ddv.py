from exactly_lib.type_system.data.described_path import DescribedPathValue
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.impl.path import described_w_handler
from exactly_lib.type_system.data.impl.path import describer_handlers


def of(path: FileRef) -> DescribedPathValue:
    return described_w_handler.DescribedPathValueWHandler(
        path,
        describer_handlers.PathDescriberHandlerForValueWithValue(path),
    )
