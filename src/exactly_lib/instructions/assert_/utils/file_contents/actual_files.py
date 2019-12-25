from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.sdv_with_validation import ObjectWithSymbolReferencesAndValidation
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.common import InstructionSourceInfo
from exactly_lib.test_case.validation import sdv_validation
from exactly_lib.test_case.validation.sdv_validation import SdvValidator
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.err_msg2 import file_or_dir_contents_headers
from exactly_lib.test_case_utils.err_msg2 import path_rendering, header_rendering
from exactly_lib.type_system.data import path_description
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor, FilePropertyDescriptorConstructor
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.strings import ToStringObject


class ComparisonActualFile(tuple):
    def __new__(cls,
                actual_path: DescribedPath,
                checked_file_describer: FilePropertyDescriptorConstructor,
                file_access_needs_to_be_verified: bool
                ):
        return tuple.__new__(cls, (checked_file_describer,
                                   actual_path,
                                   file_access_needs_to_be_verified))

    @property
    def checked_file_describer(self) -> FilePropertyDescriptorConstructor:
        return self[0]

    @property
    def path(self) -> DescribedPath:
        return self[1]

    @property
    def file_access_needs_to_be_verified(self) -> bool:
        return self[2]


class ComparisonActualFileConstructor(ObjectWithSymbolReferencesAndValidation, ABC):
    @abstractmethod
    def construct(self,
                  source_info: InstructionSourceInfo,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFile:
        pass

    @abstractmethod
    def failure_message_header(self, environment: FullResolvingEnvironment) -> Renderer[MajorBlock]:
        pass


class ConstructorForPath(ComparisonActualFileConstructor):
    def __init__(self,
                 path: PathSdv,
                 object_name: ToStringObject,
                 file_access_needs_to_be_verified: bool,
                 ):
        """

        :param path: The path of the file that represents the actual string.
        :param object_name: Tells what "path" is representing.
        :param file_access_needs_to_be_verified: Tells if the path
        referred to by "path" may be invalid (e.g. do not exist), and
        thus need to be verified before it can be used, and the result of
        this verification may be that the path is invalid and thus the
        operation must be aborted with an explaining error message.
        """
        self._path = path
        self._object_name = object_name
        self._file_access_needs_to_be_verified = file_access_needs_to_be_verified

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._path.references

    @property
    def validator(self) -> SdvValidator:
        return sdv_validation.ConstantSuccessSdvValidator()

    def construct(self,
                  source_info: InstructionSourceInfo,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFile:
        described_path = (
            self._path.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )
        return ComparisonActualFile(
            described_path,
            ActualFilePropertyDescriptorConstructorForComparisonFile(
                described_path.describer,
                str(self._object_name)),
            self._file_access_needs_to_be_verified,
        )

    def failure_message_header(self, environment: FullResolvingEnvironment) -> Renderer[MajorBlock]:
        described_path = (
            self._path.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )

        return path_rendering.HeaderAndPathMajorBlock(
            header_rendering.SimpleHeaderMinorBlockRenderer(
                file_or_dir_contents_headers.unexpected(self._object_name)
            ),
            path_rendering.PathRepresentationsRenderersForPrimitive(described_path.describer),
        )


class ActualFilePropertyDescriptorConstructorForComparisonFile(FilePropertyDescriptorConstructor):
    def __init__(self,
                 path: PathDescriberForPrimitive,
                 object_name: str):
        self._path = path
        self._object_name = object_name

    def construct_for_contents_attribute(self, contents_attribute: str) -> PropertyDescriptor:
        return path_description.path_value_description(
            property_description.file_property_name(contents_attribute, self._object_name),
            self._path,
            True,
        )
