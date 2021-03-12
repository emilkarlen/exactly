from typing import Sequence, Optional

from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.files_source.defs import ModificationType
from exactly_lib.symbol.sdv_structure import SymbolReference, TypesSymbolDependentValue, ObjectWithSymbolReferences
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.w_validation import ValidatableDdv
from exactly_lib.type_val_deps.types.files_source.ddv import FilesSourceAdv, FilesSourceDdv
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable
from . import description
from . import utils
from ...file_maker import FileMakerDdv, FileMakerSdv, FileMaker
from ... import defs


class DirFileMakerSdv(FileMakerSdv):
    def __init__(self,
                 modification: ModificationType,
                 contents: Optional[FilesSourceSdv],
                 ):
        self._modification = modification
        self._contents = contents

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ObjectWithSymbolReferences.references__optional(self._contents)

    def resolve(self, symbols: SymbolTable) -> FileMakerDdv:
        return DirFileMakerDdv(
            self._modification,
            TypesSymbolDependentValue.resolve__optional(self._contents, symbols),
        )


class DirFileMakerDdv(FileMakerDdv):
    def __init__(self,
                 modification: ModificationType,
                 contents: Optional[FilesSourceDdv],
                 ):
        self._modification = modification
        self._contents = contents
        self._contents_describer = (
            None
            if contents is None
            else contents.describer
        )

    def describer(self, file_name: str) -> DetailsRenderer:
        return description.Describer(defs.FileType.DIR,
                                     self._modification,
                                     file_name,
                                     self._contents_describer)

    @property
    def validator(self) -> DdvValidator:
        return ValidatableDdv.validator__optional(self._contents)

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[FileMaker]:
        return DirFileMakerAdv(
            self._modification,
            DirDependentValue.value_of_any_dependency__optional(self._contents, tcds),
        )


class DirFileMakerAdv(ApplicationEnvironmentDependentValue[FileMaker]):
    def __init__(self,
                 modification: ModificationType,
                 contents: FilesSourceAdv,
                 ):
        self._modification = modification
        self._contents = contents

    def primitive(self, environment: ApplicationEnvironment) -> FileMaker:
        return DirFileMaker(
            self._modification,
            ApplicationEnvironmentDependentValue.primitive__optional(self._contents, environment),
        )


class DirFileMaker(FileMaker):
    def __init__(self,
                 modification: ModificationType,
                 contents: Optional[FilesSource],
                 ):
        self._modification = modification
        self._contents = contents
        self._contents_describer = (
            None
            if contents is None
            else
            contents.describer
        )
        self._modification_maker = (
            utils.NewFileCreator(self._create_dir)
            if modification is ModificationType.CREATE
            else
            utils.ExistingFileModifier(FileType.DIRECTORY, self._add_to_dir)
        )

    def describer(self, file_name: str) -> DetailsRenderer:
        return description.Describer(defs.FileType.DIR,
                                     self._modification,
                                     file_name,
                                     self._contents_describer)

    def make(self, path: DescribedPath):
        self._modification_maker.make(path)

    def _create_dir(self, path: DescribedPath):
        path.primitive.mkdir(parents=True)
        self._populate(path)

    def _add_to_dir(self, path: DescribedPath):
        self._populate(path)

    def _populate(self, path: DescribedPath):
        if self._contents:
            self._contents.populate(path)
