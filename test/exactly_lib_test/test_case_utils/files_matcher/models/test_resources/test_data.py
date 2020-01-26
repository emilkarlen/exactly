import pathlib
from typing import List, Sequence

from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, Dir, empty_file, empty_dir
from exactly_lib_test.test_resources.test_utils import NEA, EA

FILE_SYS__EMPTY = ()

FILE_SYS__WITH_4_LEVELS = (
    empty_file('a1'),
    empty_dir('b1 - no sub levels'),
    Dir('c1 - with sub dirs and files until depth 1', [
        empty_file('ca2'),
        empty_dir('cb2'),
    ]),
    Dir('d1 - with sub dirs until depth 4', [
        empty_file('da2'),
        empty_dir('db2'),
        Dir('dc2', [
            empty_file('dca3'),
            empty_dir('dcb3'),
            Dir('dcc3', [
                empty_dir('dcca4'),
                empty_file('dccb4'),
            ])
        ])
    ]),
    Dir('e1 - dir with only dirs until depth 4',
        [Dir('ea2',
             [Dir('eaa3',
                  [empty_dir('eaaa4')])])]
        ),
    Dir('f1 - dir with only dirs until depth 3',
        [Dir('fa2',
             [empty_dir('faa3')])]
        ),
    Dir('g1 - dir with only dirs until depth 2',
        [empty_dir('ga2')]
        ),
)

DEPTH_TEST_MODELS = (
    NameAndValue(
        'empty',
        FILE_SYS__EMPTY,
    ),
    NameAndValue(
        'with 4 levels',
        FILE_SYS__WITH_4_LEVELS,
    )
)


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


def strip_file_type_info_s(x: Sequence[NEA[List[FileElementForTest], List[FileSystemElement]]],
                           ) -> Sequence[NEA[List[pathlib.Path], List[FileSystemElement]]]:
    return [
        strip_file_type_info_1(nea)
        for nea in x
    ]


def strip_file_type_info_1(nea: NEA[List[FileElementForTest], List[FileSystemElement]],
                           ) -> NEA[List[pathlib.Path], List[FileSystemElement]]:
    return NEA(
        nea.name,
        [
            element.relative_path
            for element in nea.expected
        ],
        nea.actual,
    )


def strip_file_type_info__ea(ea: EA[List[FileElementForTest], List[FileSystemElement]],
                             ) -> EA[List[pathlib.Path], List[FileSystemElement]]:
    return EA(
        [
            element.relative_path
            for element in ea.expected
        ],
        ea.actual,
    )


def strip_file_type_info(elements: List[FileElementForTest],
                         ) -> List[pathlib.Path]:
    return [
        element.relative_path
        for element in elements
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
    expected = _flatten_directories(pathlib.Path(), actual)

    return NEA(name, expected, actual)


def expected_is_direct_contents_of_actual(name: str,
                                          actual: List[FileSystemElement],
                                          ) -> NEA[List[FileElementForTest], List[FileSystemElement]]:
    ea = expected_is_actual_down_to_max_depth(0, actual)
    return NEA(name, ea.expected, ea.actual)


def expected_is_actual_down_to_max_depth(depth: int,
                                         actual: List[FileSystemElement],
                                         ) -> EA[List[FileElementForTest], List[FileSystemElement]]:
    expected = _flatten_directories(pathlib.Path(),
                                    include_until_max_depth(depth, actual))

    return EA(expected, actual)


def expected_is_actual_from_min_depth(min_depth: int,
                                      actual: List[FileSystemElement],
                                      ) -> EA[List[FileElementForTest], List[FileSystemElement]]:
    expected = _flatten_directories(pathlib.Path(),
                                    actual,
                                    inclusion_min_depth=min_depth,
                                    )

    return EA(expected, actual)


def expected_is_actual_within_depth_limits(min_depth: int,
                                           max_depth: int,
                                           actual: List[FileSystemElement],
                                           ) -> EA[List[FileElementForTest], List[FileSystemElement]]:
    expected = _flatten_directories(pathlib.Path(),
                                    include_until_max_depth(max_depth, actual),
                                    inclusion_min_depth=min_depth,
                                    )

    return EA(expected, actual)


def include_until_max_depth(n: int,
                            elements: List[FileSystemElement]) -> List[FileSystemElement]:
    if n == -1:
        return []
    else:
        return [
            (
                Dir(e.name, include_until_max_depth(n - 1, e.file_system_element_contents))
                if isinstance(e, Dir)
                else
                e
            )
            for e in elements
        ]


def _flatten_directories(root: pathlib.Path,
                         elements: List[FileSystemElement],
                         inclusion_min_depth: int = 0,
                         current_depth: int = 0,
                         ) -> List[FileElementForTest]:
    ret_val = []
    satisfies_min_depth_limit = current_depth >= inclusion_min_depth
    for element in elements:
        if satisfies_min_depth_limit:
            ret_val.append(
                FileElementForTest(root / element.name,
                                   element.file_type)
            )
        if isinstance(element, Dir):
            ret_val += _flatten_directories(root / element.name,
                                            element.file_system_element_contents,
                                            inclusion_min_depth=inclusion_min_depth,
                                            current_depth=current_depth + 1)

    return ret_val
