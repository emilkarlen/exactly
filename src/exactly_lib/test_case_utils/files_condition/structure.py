"""
FilesCondition - a set of file names, each with an optional `FileMatcher`.
"""
from pathlib import PurePosixPath
from typing import Sequence, Optional, Tuple, Mapping

from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.described_dep_val import LogicWithDescriberSdv, LogicWithDetailsDescriptionDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.description.details_structured import WithDetailsDescription
from exactly_lib.type_system.logic.file_matcher import FileMatcherAdv, GenericFileMatcherSdv, \
    FileMatcherDdv
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable


class FilesCondition(WithDetailsDescription):
    def __init__(self, files: Mapping[PurePosixPath, Optional[FileMatcherAdv]]):
        self._files = files

    @property
    def describer(self) -> DetailsRenderer:
        raise NotImplementedError('todo')

    @property
    def files(self) -> Mapping[PurePosixPath, Optional[FileMatcherAdv]]:
        return self._files


class FilesConditionAdv(ApplicationEnvironmentDependentValue[FilesCondition]):
    def __init__(self, files: Mapping[PurePosixPath, Optional[FileMatcherAdv]]):
        self._files = files

    def primitive(self, environment: ApplicationEnvironment) -> FilesCondition:
        raise NotImplementedError('todo')


class FilesConditionDdv(LogicWithDetailsDescriptionDdv[FilesCondition]):
    def __init__(self, files: Sequence[Tuple[StringDdv, Optional[FileMatcherDdv]]]):
        self._files = files

    @property
    def describer(self) -> DetailsRenderer:
        raise NotImplementedError('todo')

    @property
    def validator(self) -> DdvValidator:
        raise NotImplementedError('todo')

    def value_of_any_dependency(self, tcds: Tcds) -> FilesConditionAdv:
        raise NotImplementedError('todo')


class FilesConditionSdv(LogicWithDescriberSdv[FilesCondition]):
    def __init__(self, files: Sequence[Tuple[StringSdv, Optional[GenericFileMatcherSdv]]]):
        self._files = files

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('todo')

    def resolve(self, symbols: SymbolTable) -> FilesConditionDdv:
        raise NotImplementedError('todo')
