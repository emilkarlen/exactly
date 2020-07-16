from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.symbol import sdv_validation
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.sdv_validation import SdvValidator
from exactly_lib.symbol.sdv_with_validation import ObjectWithSymbolReferencesAndSdvValidation
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import instruction_environment as i
from exactly_lib.test_case_utils.err_msg import file_or_dir_contents_headers, path_rendering, header_rendering
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.str_.str_constructor import ToStringObject


class ComparisonActualFile(tuple):
    def __new__(cls,
                actual_path: DescribedPath,
                file_access_needs_to_be_verified: bool
                ):
        return tuple.__new__(cls, (actual_path,
                                   file_access_needs_to_be_verified))

    @property
    def path(self) -> DescribedPath:
        return self[0]

    @property
    def file_access_needs_to_be_verified(self) -> bool:
        return self[1]


class ComparisonActualFileConstructor(ObjectWithSymbolReferencesAndSdvValidation, ABC):
    @abstractmethod
    def construct(self,
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  ) -> ComparisonActualFile:
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
                  environment: i.InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices) -> ComparisonActualFile:
        described_path = (
            self._path.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )
        return ComparisonActualFile(
            described_path,
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
