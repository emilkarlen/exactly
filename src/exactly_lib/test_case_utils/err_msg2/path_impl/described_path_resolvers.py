from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathResolver
from exactly_lib.test_case_utils.err_msg2.path_impl import described_path_w_handler
from exactly_lib.test_case_utils.err_msg2.path_impl import path_describer_handlers


def of(path_resolver: FileRefResolver) -> DescribedPathResolver:
    return described_path_w_handler.DescribedPathResolverWHandler(
        path_resolver,
        path_describer_handlers.PathDescriberHandlerForResolverWithResolver(path_resolver),
    )
