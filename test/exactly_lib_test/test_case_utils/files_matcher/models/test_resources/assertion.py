import pathlib
import unittest
from pathlib import Path
from typing import List, Callable

from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, Dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, MessageBuilder


class ModelContentsAssertion(ValueAssertionBase[FilesMatcherModel]):
    def __init__(self,
                 contents_root: pathlib.Path,
                 expected_paths__rel_root: List[pathlib.Path],
                 ):
        self._contents_root = contents_root
        self._expected_paths__rel_root = sorted(expected_paths__rel_root)

    def _apply(self,
               put: unittest.TestCase,
               value: FilesMatcherModel,
               message_builder: MessageBuilder):
        actual__rel_contents_root = self._actual_paths__rel_contents_root(value)

        asrt.equals(self._expected_paths__rel_root).apply(
            put,
            actual__rel_contents_root,
            message_builder.for_sub_component('paths rel contents root')
        )

        expected__absolute = self._expected_paths__absolute()
        actual__absolute = self._actual_paths__absolute(value)

        asrt.equals(expected__absolute).apply(
            put,
            actual__absolute,
            message_builder.for_sub_component('absolute paths')
        )

    @staticmethod
    def _actual_paths__rel_contents_root(model: FilesMatcherModel) -> List[Path]:
        ret_val = [
            f.relative_to_root_dir
            for f in model.files()
        ]
        ret_val.sort()
        return ret_val

    @staticmethod
    def _actual_paths__absolute(model: FilesMatcherModel) -> List[Path]:
        ret_val = [
            f.path.primitive
            for f in model.files()
        ]
        ret_val.sort()
        return ret_val

    def _expected_paths__absolute(self) -> List[Path]:
        return [
            self._contents_root / rel_contents_root
            for rel_contents_root in self._expected_paths__rel_root
        ]


def _paths_rel_root(root: Path,
                    contents: List[FileSystemElement],
                    files_type_is_included: Callable[[FileType], bool],
                    ) -> List[Path]:
    ret_val = []
    for element in contents:
        if files_type_is_included(element.file_type):
            ret_val.append(root / element.name)
        if isinstance(element, Dir):
            ret_val += _paths_rel_root(root / element.name,
                                       element.file_system_element_contents,
                                       files_type_is_included)

    return ret_val
