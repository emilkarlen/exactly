from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.type_system.data.file_ref import DescribedPathPrimitive
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor, FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.string_matcher import FileToCheck, DestinationFilePathGetter
from exactly_lib.type_system.logic.string_transformer import IdentityStringTransformer
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand, TmpDirFileSpace
from exactly_lib_test.test_case_utils.err_msg.test_resources import described_path


class ModelBuilder:
    """Builder of :class:`FileToCheck` attributes."""

    def __init__(self):
        self.original_file_contents = ''

    def with_original_file_contents(self, contents: str):
        self.original_file_contents = contents
        return self


def empty_model() -> ModelBuilder:
    return ModelBuilder()


def model_of(contents: str) -> ModelBuilder:
    return ModelBuilder().with_original_file_contents(contents)


def arbitrary_model() -> ModelBuilder:
    return empty_model()


class ModelConstructor:
    """Constructs a :class:^FileToCheck^ given an environment with existing directories"""

    def __init__(self,
                 model_builder: ModelBuilder,
                 sds: SandboxDirectoryStructure):
        self.model_builder = model_builder
        self.sds = sds

    def construct(self) -> FileToCheck:
        tmp_dir_file_space = TmpDirFileSpaceAsDirCreatedOnDemand(self.sds.internal_tmp_dir)
        original_file_path = self._create_original_file(tmp_dir_file_space)

        return FileToCheck(
            original_file_path,
            _FilePropertyDescriptorConstructorForTestImpl('file-with-original-contents'),
            tmp_dir_file_space,
            IdentityStringTransformer(),
            DestinationFilePathGetter(),
        )

    def _create_original_file(self, file_space: TmpDirFileSpace) -> DescribedPathPrimitive:
        original_file_path = file_space.new_path()

        with original_file_path.open(mode='w') as f:
            f.write(self.model_builder.original_file_contents)

        return described_path.new_primitive(original_file_path)


class _FilePropertyDescriptorConstructorForTestImpl(FilePropertyDescriptorConstructor):
    def __init__(self, name: str):
        self.name = name

    def construct_for_contents_attribute(self, contents_attribute: str) -> PropertyDescriptor:
        full_name = self.name + '/' + contents_attribute
        return property_description.property_descriptor_with_just_a_constant_name(full_name)
