from typing import Sequence, Optional

from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.files_source.defs import ModificationType
from exactly_lib.impls.types.string_source import constant_str
from exactly_lib.symbol.sdv_structure import SymbolReference, TypesSymbolDependentValue, ObjectWithSymbolReferences
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.w_validation import ValidatableDdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv, StringSourceAdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable
from . import description
from . import utils
from ...file_maker import FileMakerDdv, FileMakerSdv, FileMaker
from ... import defs


class RegularFileMakerSdv(FileMakerSdv):
    def __init__(self,
                 modification: ModificationType,
                 contents: Optional[StringSourceSdv],
                 ):
        self._modification = modification
        self._contents = contents

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ObjectWithSymbolReferences.references__optional(self._contents)

    def resolve(self, symbols: SymbolTable) -> FileMakerDdv:
        return RegularFileMakerDdv(
            self._modification,
            TypesSymbolDependentValue.resolve__optional(self._contents, symbols),
        )


class RegularFileMakerDdv(FileMakerDdv):
    def __init__(self,
                 modification: ModificationType,
                 contents: Optional[StringSourceDdv],
                 ):
        self._modification = modification
        self._contents = contents
        self._contents_describer = (
            None
            if contents is None
            else custom_details.WithTreeStructure(contents)
        )

    def describer(self, file_name: str) -> DetailsRenderer:
        return description.Describer(defs.FileType.REGULAR,
                                     self._modification,
                                     file_name,
                                     self._contents_describer)

    @property
    def validator(self) -> DdvValidator:
        return ValidatableDdv.validator__optional(self._contents)

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[FileMaker]:
        return RegularFileMakerAdv(self._modification,
                                   DirDependentValue.value_of_any_dependency__optional(self._contents, tcds),
                                   )


class RegularFileMakerAdv(ApplicationEnvironmentDependentValue[FileMaker]):
    def __init__(self,
                 modification: ModificationType,
                 contents: Optional[StringSourceAdv],
                 ):
        self._modification = modification
        self._optional_contents = contents

    def primitive(self, environment: ApplicationEnvironment) -> FileMaker:
        if self._optional_contents is None:
            return RegularFileMaker(
                self._modification,
                constant_str.string_source('', environment.tmp_files_space),
                None,
            )
        else:
            contents = self._optional_contents.primitive(environment)
            return RegularFileMaker(
                self._modification,
                contents,
                custom_details.TreeStructure(contents.structure())
            )

    def _contents(self, environment: ApplicationEnvironment) -> StringSource:
        return (
            constant_str.string_source('', environment.tmp_files_space)
            if self._optional_contents is None
            else
            self._optional_contents.primitive(environment)
        )

    def _contents_description(self, environment: ApplicationEnvironment) -> StringSource:
        return (
            constant_str.string_source('', environment.tmp_files_space)
            if self._optional_contents is None
            else
            self._optional_contents.primitive(environment)
        )


class RegularFileMaker(FileMaker):
    def __init__(self,
                 modification: ModificationType,
                 contents: StringSource,
                 contents_description: Optional[DetailsRenderer],
                 ):
        self._modification = modification
        self._contents = contents
        self._contents_description = contents_description
        self._maker = (
            utils.NewFileCreator(self._create_file)
            if modification is ModificationType.CREATE
            else
            utils.ExistingFileModifier(FileType.REGULAR,
                                       self._append_to_file)
        )

    def describer(self, file_name: str) -> DetailsRenderer:
        return description.Describer(defs.FileType.REGULAR,
                                     self._modification,
                                     file_name,
                                     self._contents_description)

    def make(self, path: DescribedPath):
        self._maker.make(path)

    def _create_file(self, path: DescribedPath):
        self._ensure_parent_dir_exists(path)
        self._write('x', path)

    def _append_to_file(self, path: DescribedPath):
        self._write('a', path)

    def _write(self, mode: str, path: DescribedPath):
        with path.primitive.open(mode) as f:
            self._contents.contents().write_to(f)

    @staticmethod
    def _ensure_parent_dir_exists(path: DescribedPath):
        parent = path.primitive.parent
        parent.mkdir(parents=True,
                     exist_ok=True)
