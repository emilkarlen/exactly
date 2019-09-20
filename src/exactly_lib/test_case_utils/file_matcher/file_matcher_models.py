from typing import List

from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessagePartConstructor
from exactly_lib.test_case_utils.err_msg2 import path_rendering
from exactly_lib.type_system import error_message
from exactly_lib.type_system.data.described_path import DescribedPathPrimitive
from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.util.file_utils import TmpDirFileSpace


class FileMatcherModelForPrimitivePath(FileMatcherModel):
    def __init__(self,
                 tmp_file_space: TmpDirFileSpace,
                 path: DescribedPathPrimitive):
        super().__init__(tmp_file_space, path)

    @property
    def file_descriptor(self) -> error_message.FilePropertyDescriptorConstructor:
        return _FilePropertyDescriptorConstructor(self.path.describer)


class FileMatcherModelForFileWithDescriptor(FileMatcherModel):
    def __init__(self,
                 tmp_file_space: TmpDirFileSpace,
                 path: DescribedPathPrimitive,
                 file_descriptor: error_message.FilePropertyDescriptorConstructor):
        super().__init__(tmp_file_space, path)
        self._file_descriptor = file_descriptor

    @property
    def file_descriptor(self) -> error_message.FilePropertyDescriptorConstructor:
        return self._file_descriptor


class _FilePropertyDescriptorConstructor(error_message.FilePropertyDescriptorConstructor):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def construct_for_contents_attribute(self, contents_attribute: str) -> error_message.PropertyDescriptor:
        from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptorWithConstantPropertyName
        path = self._path

        class _ErrorMessagePartConstructor(ErrorMessagePartConstructor):
            def lines(self) -> List[str]:
                return path_rendering.path_strings(path)

        return PropertyDescriptorWithConstantPropertyName(contents_attribute,
                                                          _ErrorMessagePartConstructor())
