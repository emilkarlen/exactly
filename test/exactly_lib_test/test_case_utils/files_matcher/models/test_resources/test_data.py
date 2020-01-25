import pathlib
from typing import List, Sequence

from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, Dir, empty_file, empty_dir
from exactly_lib_test.test_resources.test_utils import NEA


def cases() -> Sequence[NameAndValue[List[FileSystemElement]]]:
    return [
        NameAndValue(
            'empty',
            [],
        ),
        NameAndValue(
            'single regular file',
            [empty_file('an-empty-file')],
        ),
        NameAndValue(
            'single empty dir',
            [empty_dir('an-empty-dir')],
        ),
        NameAndValue(
            'directory with contents - one level',
            [
                empty_file('an-empty-file'),
                Dir('non-empty-dir',
                    [
                        empty_file('file-in-dir'),
                        empty_dir('dir-in-dir'),
                    ]),
            ]
        ),
        NameAndValue(
            'directory with contents - multiple levels',
            [
                Dir('non-empty-dir-1',
                    [empty_file('file-in-dir-1')]
                    ),
                Dir('non-empty-dir-2',
                    [
                        empty_file('file-in-dir-2'),
                        Dir('non-empty-dir-2-1',
                            [
                                empty_file('file-in-dir-2-1'),
                                empty_dir('dir-in-dir-2-1'),
                            ])
                    ]
                    ),
            ]
        ),
    ]


class FileElementForTest:
    def __init__(self,
                 relative_path: pathlib.Path,
                 file_type: FileType,
                 ):
        self.relative_path = relative_path
        self.file_type = file_type


def strip_file_type_info(x: Sequence[NEA[List[FileElementForTest], List[FileSystemElement]]],
                         ) -> Sequence[NEA[List[pathlib.Path], List[FileSystemElement]]]:
    return [
        NEA(
            nea.name,
            [
                element.relative_path
                for element in nea.expected
            ],
            nea.actual,
        )
        for nea in x
    ]


def filter_on_file_type(file_type_to_include: FileType,
                        x: Sequence[NEA[List[FileElementForTest], List[FileSystemElement]]],
                        ) -> Sequence[NEA[List[FileElementForTest], List[FileSystemElement]]]:
    return [
        NEA(
            nea.name,
            [
                element
                for element in nea.expected
                if element.file_type is file_type_to_include
            ],
            nea.actual,
        )
        for nea in x
    ]


def filter_on_base_name_prefix(prefix_to_include: str,
                               x: Sequence[NEA[List[FileElementForTest], List[FileSystemElement]]],
                               ) -> Sequence[NEA[List[FileElementForTest], List[FileSystemElement]]]:
    return [
        NEA(
            nea.name,
            [
                element
                for element in nea.expected
                if element.relative_path.name.startswith(prefix_to_include)
            ],
            nea.actual,
        )
        for nea in x
    ]


def identical_expected_and_actual(name: str,
                                  actual: List[FileSystemElement],
                                  ) -> NEA[List[FileElementForTest], List[FileSystemElement]]:
    expected = _flatten_directories(pathlib.Path('.'), actual)

    return NEA(name, expected, actual)


def expected_is_first_level_of_actual(name: str,
                                      actual: List[FileSystemElement],
                                      ) -> NEA[List[FileElementForTest], List[FileSystemElement]]:
    expected = [
        FileElementForTest(pathlib.Path(element.name),
                           element.file_type)
        for element in actual
    ]

    return NEA(name, expected, actual)


def _flatten_directories(root: pathlib.Path,
                         contents: List[FileSystemElement],
                         ) -> List[FileElementForTest]:
    ret_val = []
    for element in contents:
        ret_val.append(
            FileElementForTest(root / element.name,
                               element.file_type)
        )
        if isinstance(element, Dir):
            ret_val += _flatten_directories(root / element.name,
                                            element.file_system_element_contents)

    return ret_val
