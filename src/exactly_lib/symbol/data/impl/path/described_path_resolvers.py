from exactly_lib.symbol.data.described_path import DescribedPathResolver
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.impl.path import describer_handlers, described_w_handler


def of(path_resolver: FileRefResolver) -> DescribedPathResolver:
    return described_w_handler.DescribedPathResolverWHandler(
        path_resolver,
        describer_handlers.PathDescriberHandlerForResolverWithResolver(path_resolver),
    )
