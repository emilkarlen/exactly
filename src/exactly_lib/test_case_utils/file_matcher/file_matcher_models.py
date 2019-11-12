from abc import ABC
from typing import List

from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessagePartConstructor
from exactly_lib.test_case_utils.err_msg2 import path_rendering
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive
from exactly_lib.type_system.err_msg import prop_descr
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.util.file_utils import TmpDirFileSpace


class _FileMatcherModelImplBase(FileMatcherModel, ABC):
    def __init__(self,
                 tmp_file_space: TmpDirFileSpace,
                 path: DescribedPathPrimitive):
        self._tmp_file_space = tmp_file_space
        self._path = path

    @property
    def tmp_file_space(self) -> TmpDirFileSpace:
        return self._tmp_file_space

    @property
    def path(self) -> DescribedPathPrimitive:
        """Path of the file to match. May or may not exist."""
        return self._path


class FileMatcherModelForPrimitivePath(_FileMatcherModelImplBase):
    def __init__(self,
                 tmp_file_space: TmpDirFileSpace,
                 path: DescribedPathPrimitive):
        super().__init__(tmp_file_space, path)

    @property
    def file_descriptor(self) -> prop_descr.FilePropertyDescriptorConstructor:
        return _FilePropertyDescriptorConstructor(self.path.describer)


class FileMatcherModelForFileWithDescriptor(_FileMatcherModelImplBase):
    def __init__(self,
                 tmp_file_space: TmpDirFileSpace,
                 path: DescribedPathPrimitive,
                 file_descriptor: prop_descr.FilePropertyDescriptorConstructor):
        super().__init__(tmp_file_space, path)
        self._file_descriptor = file_descriptor

    @property
    def file_descriptor(self) -> prop_descr.FilePropertyDescriptorConstructor:
        return self._file_descriptor


class _FilePropertyDescriptorConstructor(prop_descr.FilePropertyDescriptorConstructor):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def construct_for_contents_attribute(self,
                                         contents_attribute: str) -> prop_descr.PropertyDescriptor:
        from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptorWithConstantPropertyName
        path = self._path

        class _ErrorMessagePartConstructor(ErrorMessagePartConstructor):
            def lines(self) -> List[str]:
                return path_rendering.path_strings(path)

        return PropertyDescriptorWithConstantPropertyName(contents_attribute,
                                                          _ErrorMessagePartConstructor())
