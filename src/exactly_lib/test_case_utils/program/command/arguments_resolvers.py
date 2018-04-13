from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.file_ref_check import FileRefCheckValidator, FileRefCheck


def empty() -> ArgumentsResolver:
    return ArgumentsResolver(list_resolvers.empty(),
                             ())


def new_without_validation(arguments: ListResolver) -> ArgumentsResolver:
    return ArgumentsResolver(arguments, ())


def ref_to_file_that_must_exist(file_that_must_exist: FileRefResolver,
                                file_type: FileType = FileType.REGULAR) -> ArgumentsResolver:
    file_validator = FileRefCheckValidator(FileRefCheck(file_that_must_exist,
                                                        file_properties.must_exist_as(file_type)))
    return ArgumentsResolver(list_resolvers.from_string(string_resolvers.from_file_ref_resolver(file_that_must_exist)),
                             [file_validator])
