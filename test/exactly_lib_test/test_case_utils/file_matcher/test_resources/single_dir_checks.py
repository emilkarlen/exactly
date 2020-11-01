import pathlib
import tempfile
from contextlib import contextmanager

from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForDescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.util.file_utils.misc_utils import resolved_path
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents, Dir
from exactly_lib_test.type_val_deps.types.path.test_resources import described_path


class SingleDirSetup:
    def __init__(self, action_dir_path: pathlib.Path):
        self.action_dir_path = described_path.new_primitive(action_dir_path)

    def model_with_action_dir_as_path_to_match(self) -> FileMatcherModel:
        return FileMatcherModelForDescribedPath(self.action_dir_path)

    def model_with_file_in_action_dir_as_path_to_match(self, file_name: str) -> FileMatcherModel:
        return FileMatcherModelForDescribedPath(self.action_dir_path.child(file_name))


@contextmanager
def single_dir_setup(contents: DirContents = empty_dir_contents()) -> SingleDirSetup:
    action_dir = Dir('act',
                     contents.file_system_elements)
    tmp_dir_contents = DirContents([
        action_dir
    ])
    with tempfile.TemporaryDirectory() as dir_name:
        dir_path = resolved_path(dir_name)
        tmp_dir_contents.write_to(dir_path)
        yield SingleDirSetup(
            dir_path / action_dir.name,
        )
