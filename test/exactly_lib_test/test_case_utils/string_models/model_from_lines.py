import pathlib
import unittest
from contextlib import contextmanager
from typing import Iterator, ContextManager, Sequence

from exactly_lib.test_case_utils.string_models.model_from_lines import StringModelFromLinesBase
from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace
from exactly_lib_test.test_resources.files import tmp_dir
from exactly_lib_test.util.test_resources.tmp_file_space import TmpFileSpaceThatAllowsSinglePathGeneration


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(Test)
    ])


class Test(unittest.TestCase):
    def test_as_lines(self):
        # ARRANGE #
        with tmp_dir.tmp_dir() as storage_dir:
            tmp_file_space = TmpFileSpaceThatAllowsSinglePathGeneration(
                self,
                storage_dir,
                'path-name',
            )
            model_lines = [
                '1st\n',
                '2nd\n',
            ]
            model = _ModelTestImpl(
                model_lines,
                tmp_file_space,
            )

            # ACT #

            with model.as_lines as lines:
                actual_lines__invokation_1 = list(lines)
            with model.as_lines as lines:
                actual_lines__invokation_2 = list(lines)

            # ASSERT #

            self.assertEqual(
                model_lines,
                actual_lines__invokation_1,
                'Lines, from invokation 1',
            )

            self.assertEqual(
                model_lines,
                actual_lines__invokation_2,
                'Lines, from invokation 2',
            )

            self.assertEqual(
                0,
                len(list(storage_dir.iterdir())),
                'No files should have been created in the storage dir',
            )

    def test_as_file(self):
        # ARRANGE #
        with tmp_dir.tmp_dir() as storage_dir:
            tmp_file_space = TmpFileSpaceThatAllowsSinglePathGeneration(
                self,
                storage_dir,
                'path-name',
            )
            model_lines = [
                '1st\n',
                '2nd\n',
            ]
            model = _ModelTestImpl(
                model_lines,
                tmp_file_space,
            )

            # ACT #

            path__invokation_1 = model.as_file
            path__invokation_2 = model.as_file

            # ASSERT #

            self.assertEqual(
                [tmp_file_space.storage_dir / tmp_file_space.path_name],
                list(storage_dir.iterdir()),
                'A single file should have been created in the storage dir',
            )

            self.assertEqual(
                path__invokation_1,
                path__invokation_2,
                'Both invocations should give the same path')

            actual_lines_of_path = _lines_of_file(path__invokation_1)

            self.assertEqual(
                model_lines,
                actual_lines_of_path,
                'Contents of the file (as lines)',
            )

    def test_as_lines_then_as_file(self):
        # ARRANGE #
        with tmp_dir.tmp_dir() as storage_dir:
            tmp_file_space = TmpFileSpaceThatAllowsSinglePathGeneration(
                self,
                storage_dir,
                'the-path-name',
            )
            model_lines = [
                '1st\n',
                '2nd\n',
                '3rd\n',
            ]
            model = _ModelTestImpl(
                model_lines,
                tmp_file_space,
            )

            # ACT #

            with model.as_lines as lines:
                actual_lines = list(lines)
            actual_path = model.as_file

            # ASSERT #

            self.assertEqual(
                model_lines,
                actual_lines,
                'Lines',
            )

            self.assertEqual(
                [tmp_file_space.storage_dir / tmp_file_space.path_name],
                list(storage_dir.iterdir()),
                'A single file should have been created in the storage dir',
            )

            actual_lines_of_path = _lines_of_file(actual_path)

            self.assertEqual(
                model_lines,
                actual_lines_of_path,
                'Contents of the file (as lines)',
            )

    def test_as_file_then_as_lines(self):
        # ARRANGE #
        with tmp_dir.tmp_dir() as storage_dir:
            tmp_file_space = TmpFileSpaceThatAllowsSinglePathGeneration(
                self,
                storage_dir,
                'the-path-name',
            )
            model_lines = [
                '1st\n',
                '2nd\n',
                '3rd\n',
            ]
            model = _ModelTestImpl(
                model_lines,
                tmp_file_space,
            )

            # ACT #

            actual_path = model.as_file
            with model.as_lines as lines:
                actual_lines = list(lines)

            # ASSERT #

            self.assertEqual(
                model_lines,
                actual_lines,
                'Lines',
            )

            self.assertEqual(
                [tmp_file_space.storage_dir / tmp_file_space.path_name],
                list(storage_dir.iterdir()),
                'A single file should have been created in the storage dir',
            )

            actual_lines_of_path = _lines_of_file(actual_path)

            self.assertEqual(
                model_lines,
                actual_lines_of_path,
                'Contents of the file (as lines)',
            )


def _lines_of_file(path: pathlib.Path) -> Sequence[str]:
    with path.open() as f:
        return list(f.readlines())


class _ModelTestImpl(StringModelFromLinesBase):
    def __init__(self,
                 lines: Sequence[str],
                 tmp_file_space: TmpDirFileSpace,
                 ):
        super().__init__()
        self.lines = lines
        self.tmp_file_space = tmp_file_space

    @property
    def _tmp_file_space(self) -> TmpDirFileSpace:
        return self.tmp_file_space

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self.lines)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
