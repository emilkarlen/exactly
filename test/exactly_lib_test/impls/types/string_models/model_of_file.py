import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager

from exactly_lib.impls.types.string_models import file_model as sut
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_model.test_resources import model_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestModelFromFile(),
    ])


class TestModelFromFile(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_constructor = _ModelConstructor('the contents\nof the file')
        expectation = model_checker.Expectation.equals(
            model_constructor.contents,
            may_depend_on_external_resources=asrt.equals(True),
        )

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
            _dir_file_space_that_must_not_be_used_getter,
        )
        # ACT & ASSERT #
        checker.check()


@contextmanager
def _dir_file_space_that_must_not_be_used_getter() -> ContextManager[DirFileSpace]:
    yield DirFileSpaceThatMustNoBeUsed()


class _ModelConstructor(model_checker.ModelConstructor):
    def __init__(self, contents: str):
        self.contents = contents

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        file_with_contents = fs.File('model-file.txt', self.contents)
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir = Path(tmp_dir_name)
            fs.DirContents([file_with_contents]).write_to(tmp_dir)

            yield sut.StringModelOfFile(
                tmp_dir / file_with_contents.name,
                app_env.tmp_files_space,
            )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
