import pathlib
from typing import List

from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib_test.test_resources.files.file_structure import sym_link, FileSystemElement, \
    Dir, File

REGULAR = File.empty('regular')
EMPTY_DIR = Dir.empty('empty-directory')
SYMLINK__TO_REGULAR = sym_link('sym-link--to-regular', REGULAR.name)
SYMLINK__TO_EMPTY_DIR = sym_link('sym-link--to-empty-directory', EMPTY_DIR.name)
SYMLINK__BROKEN = sym_link('sym-link--broken', 'non-existing-target')

ALL_TYPES_OF_FILES__DEPTH_0 = [
    REGULAR,
    EMPTY_DIR,
    SYMLINK__TO_REGULAR,
    SYMLINK__TO_EMPTY_DIR,
    SYMLINK__BROKEN,
]


def _paths_of(elements: List[FileSystemElement], root: pathlib.Path = pathlib.Path()) -> List[pathlib.Path]:
    return [
        root / element.name
        for element in elements
    ]


EXPECTED__DEPTH_0 = {
    FileType.REGULAR: _paths_of([
        REGULAR,
        SYMLINK__TO_REGULAR,
    ]),
    FileType.DIRECTORY: _paths_of([
        EMPTY_DIR,
        SYMLINK__TO_EMPTY_DIR,
    ]),
    FileType.SYMLINK: _paths_of([
        SYMLINK__TO_REGULAR,
        SYMLINK__TO_EMPTY_DIR,
        SYMLINK__BROKEN,
    ]),
}

REGULAR__IN_NON_EMPTY_DIR = File.empty('regular-file-in-non-empty-dir')
SYM_LINK__BROKEN__IN_NON_EMPTY_DIR = sym_link('sym-link--broken--in-non-empty-dir', 'non-existing--in-non-empty-dir')

NON_EMPTY_DIR = Dir('non-empty-dir', [
    REGULAR__IN_NON_EMPTY_DIR,
    SYM_LINK__BROKEN__IN_NON_EMPTY_DIR,
])
SYMLINK__TO_NON_EMPTY_DIR = sym_link('sym-link--to-non-empty-directory', NON_EMPTY_DIR.name)

ACTUAL__RECURSIVE__DEPTH_1 = (
        ALL_TYPES_OF_FILES__DEPTH_0 +
        [
            NON_EMPTY_DIR,
            SYMLINK__TO_NON_EMPTY_DIR,
        ]
)

EXPECTED__DEPTH_1 = {
    FileType.REGULAR: (
            _paths_of([
                REGULAR,
                SYMLINK__TO_REGULAR,
            ]) +
            _paths_of([
                REGULAR__IN_NON_EMPTY_DIR,
            ],
                root=NON_EMPTY_DIR.name_as_path,
            ) +
            _paths_of([
                REGULAR__IN_NON_EMPTY_DIR,
            ],
                root=SYMLINK__TO_NON_EMPTY_DIR.name_as_path,
            )
    ),
    FileType.DIRECTORY: (
            _paths_of([
                EMPTY_DIR,
                SYMLINK__TO_EMPTY_DIR,
                NON_EMPTY_DIR,
                SYMLINK__TO_NON_EMPTY_DIR,
            ]) +
            _paths_of([

            ],
                root=NON_EMPTY_DIR.name_as_path)
    ),
    FileType.SYMLINK: (
            _paths_of([
                SYMLINK__TO_REGULAR,
                SYMLINK__TO_EMPTY_DIR,
                SYMLINK__BROKEN,
                SYMLINK__TO_NON_EMPTY_DIR,
            ]) +
            _paths_of([
                SYM_LINK__BROKEN__IN_NON_EMPTY_DIR,
            ],
                root=NON_EMPTY_DIR.name_as_path
            ) +
            _paths_of([
                SYM_LINK__BROKEN__IN_NON_EMPTY_DIR,
            ],
                root=SYMLINK__TO_NON_EMPTY_DIR.name_as_path
            )
    ),
}
