import pathlib
from typing import Sequence

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile, \
    FilePropertyDescriptorConstructor
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileToCheck, \
    DestinationFilePathGetter
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException, PfhHardErrorException
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg import diff_msg_utils, diff_msg
from exactly_lib.test_case_utils.err_msg import path_description
from exactly_lib.type_system.data.file_ref import FileRef


class ResolvedComparisonActualFile(tuple):
    def __new__(cls,
                actual_file_path: pathlib.Path,
                actual_file: FileRef,
                checked_file_describer: FilePropertyDescriptorConstructor,
                ):
        return tuple.__new__(cls, (actual_file_path, checked_file_describer, actual_file))

    @property
    def actual_file_path(self) -> pathlib.Path:
        return self[0]

    @property
    def checked_file_describer(self) -> FilePropertyDescriptorConstructor:
        return self[1]

    @property
    def actual_file(self) -> FileRef:
        return self[2]


class FileExistenceAssertionPart(AssertionPart):
    """
    Checks existence of a :class:`ComparisonActualFile`,

    and returns it's path, if it exists.

    :raises PfhFailException: File does not exist.
    """

    def __init__(self, actual_file: ComparisonActualFile):
        super().__init__()
        self._actual_file = actual_file

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._actual_file.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              not_used,
              ) -> ResolvedComparisonActualFile:
        """
        :return: The resolved path
        """
        failure_message = self._actual_file.file_check_failure(environment)
        if failure_message:
            raise PfhFailException(failure_message)

        actual_path_value = self._actual_file.file_ref_resolver().resolve(environment.symbols)
        return ResolvedComparisonActualFile(actual_path_value.value_of_any_dependency(environment.home_and_sds),
                                            actual_path_value,
                                            self._actual_file.property_descriptor_constructor)


class FileTransformerAsAssertionPart(AssertionPart):
    """
    Transforms a given existing file.

    Does not check any property.

    :raises PfhPfhHardErrorException: The transformation fails
    """

    def __init__(self, lines_transformer_resolver: LinesTransformerResolver):
        super().__init__()
        self._lines_transformer_resolver = lines_transformer_resolver
        self._destination_file_path_getter = DestinationFilePathGetter()

        self._file_prop_check = file_properties.ActualFilePropertiesResolver(file_properties.FileType.REGULAR,
                                                                             follow_symlinks=True)

    @property
    def references(self) -> list:
        return self._lines_transformer_resolver.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_transform: ResolvedComparisonActualFile,
              ) -> FileToCheck:
        """
        :param file_to_transform: The file that should be transformed
        :return: The path of the transformed file.
        """
        actual_file_path = file_to_transform.actual_file_path
        failure_info_properties = self._file_prop_check.resolve_failure_info(file_to_transform.actual_file_path)

        if failure_info_properties:
            err_msg = self._err_msg(environment, file_to_transform, failure_info_properties)
            raise PfhHardErrorException(err_msg)

        lines_transformer = self._lines_transformer_resolver.resolve(environment.symbols)
        return FileToCheck(actual_file_path,
                           file_to_transform.checked_file_describer,
                           environment,
                           lines_transformer,
                           self._destination_file_path_getter)

    def _err_msg(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 file_to_transform: ResolvedComparisonActualFile,
                 actual_file_properties: file_properties.Properties) -> str:
        from exactly_lib.symbol.data.value_resolvers.file_ref_resolvers import FileRefConstant
        from exactly_lib.util.logic_types import ExpectationType

        def actual_info_single_line_value() -> str:
            return file_properties.render_property(actual_file_properties)

        property_descriptor = path_description.path_value_description(
            actual_files.PLAIN_FILE_OBJECT_NAME,
            FileRefConstant(file_to_transform.actual_file))
        diff_failure_resolver = diff_msg_utils.DiffFailureInfoResolver(
            property_descriptor,
            ExpectationType.POSITIVE,
            diff_msg_utils.ConstantExpectedValueResolver('existing regular file'),
        )
        actual_info = diff_msg.ActualInfo(actual_info_single_line_value())
        return diff_failure_resolver.resolve(environment, actual_info).error_message()
