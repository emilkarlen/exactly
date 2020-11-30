import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager

from exactly_lib.impls.types.string_model import file_model as sut
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib_test.tcfs.test_resources import ds_construction, tcds_populators
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.path.test_resources import path_describer
from exactly_lib_test.type_val_prims.string_model.test_resources import model_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestExplicitlyDescribed(),
        TestDescribed(),
        TestPoorlyDescribed(),
    ])


class TestExplicitlyDescribed(unittest.TestCase):
    def runTest(self):
        model_constructor = _ModelConstructorOfExplicitlyDescribed('the contents\nof the file')
        _check(self, model_constructor, model_constructor.contents)


class TestDescribed(unittest.TestCase):
    def runTest(self):
        model_constructor = _ModelConstructorOfDescribed('the contents\nof the file')
        _check(self, model_constructor, model_constructor.contents)


class TestPoorlyDescribed(unittest.TestCase):
    def runTest(self):
        model_constructor = _ModelConstructorOfPoorlyDescribed('the contents\nof the file')
        _check(self, model_constructor, model_constructor.contents)


def _check(put: unittest.TestCase,
           model_constructor: model_checker.ModelConstructor,
           expected_contents: str):
    # ARRANGE #
    expectation = model_checker.Expectation.equals(
        expected_contents,
        may_depend_on_external_resources=asrt.equals(True),
    )

    checker = model_checker.Checker(
        put,
        model_constructor,
        expectation,
        _dir_file_space_that_must_not_be_used_getter,
    )
    # ACT & ASSERT #
    checker.check()


@contextmanager
def _dir_file_space_that_must_not_be_used_getter() -> ContextManager[DirFileSpace]:
    yield DirFileSpaceThatMustNoBeUsed()


class _ModelConstructorWSingleTmpFileBase(model_checker.ModelConstructor):
    def __init__(self, contents: str):
        self.contents = contents
        self._file_with_contents = fs.File('model-file.txt', self.contents)

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir = Path(tmp_dir_name)
            fs.DirContents([self._file_with_contents]).write_to(tmp_dir)

            yield sut.string_model_of_file__poorly_described(
                tmp_dir / self._file_with_contents.name,
                app_env.tmp_files_space,
            )

    def _string_model(self,
                      model_file: Path,
                      app_env: ApplicationEnvironment,
                      ) -> StringModel:
        raise NotImplementedError('abstract method')


class _ModelConstructorOfPoorlyDescribed(_ModelConstructorWSingleTmpFileBase):
    def _string_model(self,
                      model_file: Path,
                      app_env: ApplicationEnvironment,
                      ) -> StringModel:
        return sut.string_model_of_file__poorly_described(
            model_file,
            app_env.tmp_files_space,
        )


class _ModelConstructorOfExplicitlyDescribed(_ModelConstructorWSingleTmpFileBase):
    def _string_model(self,
                      model_file: Path,
                      app_env: ApplicationEnvironment,
                      ) -> StringModel:
        return sut.StringModelOfFile(
            model_file,
            path_describer.PathDescriberForPrimitiveTestImpl('the description'),
            app_env.tmp_files_space,
        )


class _ModelConstructorOfDescribed(model_checker.ModelConstructor):
    def __init__(self, contents: str):
        self.contents = contents
        file_with_contents = fs.File('model-file.txt', self.contents)
        relativity = RelOptionType.REL_TMP
        self._ddv = path_ddvs.simple_of_rel_option(relativity, file_with_contents.name)
        self._tcds_populator = tcds_populators.TcdsPopulatorForRelOptionType(
            relativity,
            fs.DirContents([file_with_contents])
        )

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        with ds_construction.tcds_with_act_as_curr_dir_2(tcds_contents=self._tcds_populator) as tcds:
            described_path = self._ddv.value_of_any_dependency__d(tcds)
            yield sut.string_model_of_file__described(
                described_path,
                app_env.tmp_files_space,
            )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
