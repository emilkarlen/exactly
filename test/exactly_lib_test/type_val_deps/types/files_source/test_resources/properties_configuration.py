import pathlib
import unittest

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_deps.types.files_source.ddv import FilesSourceDdv
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElements
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.common_properties_checker import \
    CommonPropertiesConfiguration, Applier, CommonSdvPropertiesChecker
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.sdv_checker import \
    WithDetailsDescriptionExecutionPropertiesChecker
from exactly_lib_test.type_val_deps.types.path.test_resources import described_path


class FilesSourcePropertiesConfiguration(
    CommonPropertiesConfiguration[FilesSource,
                                  FileSystemElements,
                                  pathlib.Path]):
    def __init__(self):
        self._applier = _ApplierThatExecutesInTmpDir()

    def applier(self) -> Applier[FilesSource, FileSystemElements, pathlib.Path]:
        return self._applier

    def new_sdv_checker(self) -> CommonSdvPropertiesChecker[FilesSource]:
        return _SdvPropertiesChecker()

    def new_execution_checker(self) -> WithDetailsDescriptionExecutionPropertiesChecker[FilesSource, pathlib.Path]:
        return WithDetailsDescriptionExecutionPropertiesChecker(
            FilesSourceDdv,
            FilesSource,
            asrt.anything_goes(),
        )


class _SdvPropertiesChecker(CommonSdvPropertiesChecker[FilesSource]):
    def check(self,
              put: unittest.TestCase,
              actual: FullDepsSdv[FilesSource],
              message_builder: MessageBuilder,
              ):
        asrt.is_instance(FilesSourceSdv).apply(
            put,
            actual,
            message_builder
        )


class _ApplierThatExecutesInTmpDir(Applier[FilesSource, FileSystemElements, pathlib.Path]):
    NON_SDS_ROOT_FILE_NAME = 'files-source-tmp-dir'

    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: FilesSource,
              resolving_environment: FullResolvingEnvironment,
              input_: FileSystemElements) -> pathlib.Path:
        dir_arrangement = fs.DirContents([
            fs.Dir(self.NON_SDS_ROOT_FILE_NAME,
                   list(input_))
        ])

        existing_dir = resolving_environment.tcds.sds.root_dir

        dir_arrangement.write_to(existing_dir)

        population_dir = existing_dir / self.NON_SDS_ROOT_FILE_NAME

        primitive.populate(described_path.new_primitive(population_dir))

        return population_dir
