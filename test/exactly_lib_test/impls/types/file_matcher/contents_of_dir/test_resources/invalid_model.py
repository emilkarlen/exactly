from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents, sym_link, \
    File


def cases(model_file_name: str) -> Sequence[NameAndValue[DirContents]]:
    return [
        NameAndValue(
            'file does not exist',
            empty_dir_contents(),
        ),
        NameAndValue(
            'file is regular file',
            DirContents([
                File.empty(model_file_name)
            ]),
        ),
        NameAndValue(
            'file is broken sym link',
            DirContents([
                sym_link(model_file_name, 'non-existing-target')
            ]),
        ),
        NameAndValue(
            'file is sym link to regular file',
            DirContents([
                sym_link(model_file_name, 'regular file'),
                File.empty('regular file')
            ]),
        ),
    ]
