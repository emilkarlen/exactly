import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager

from exactly_lib.impls.types.string_source import file_source as sut
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib_test.tcfs.test_resources import ds_construction, tcds_populators
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.types.path.test_resources import path_describer
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import \
    SourceConstructorWAppEnvForTest


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestExplicitlyDescribed(),
        TestDescribed(),
        TestPoorlyDescribed(),
    ])


class TestExplicitlyDescribed(unittest.TestCase):
    def runTest(self):
        source_constructor = _SourceConstructorOfExplicitlyDescribed('the contents\nof the file')
        _check(self, source_constructor, source_constructor.contents)


class TestDescribed(unittest.TestCase):
    def runTest(self):
        source_constructor = _SourceConstructorOfDescribed('the contents\nof the file')
        _check(self, source_constructor, source_constructor.contents)


class TestPoorlyDescribed(unittest.TestCase):
    def runTest(self):
        source_constructor = _SourceConstructorOfPoorlyDescribed('the contents\nof the file')
        _check(self, source_constructor, source_constructor.contents)


def _check(put: unittest.TestCase,
           source_constructor: multi_obj_assertions.SourceConstructor,
           expected_contents: str):
    # ARRANGE #
    expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
        expected_contents,
        may_depend_on_external_resources=asrt.equals(True),
        frozen_may_depend_on_external_resources=asrt.equals(True),
    )

    assertions = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
    # ACT & ASSERT #
    assertions.apply_without_message(
        put,
        multi_obj_assertions.SourceConstructors.of_common(source_constructor),
    )


@contextmanager
def _dir_file_space_that_must_not_be_used_getter(put: unittest.TestCase,
                                                 message_builder: MessageBuilder) -> ContextManager[DirFileSpace]:
    yield DirFileSpaceThatMustNoBeUsed(message_builder.apply('dir-file-space'))


class _SourceConstructorWSingleTmpFileBase(SourceConstructorWAppEnvForTest):
    def __init__(self, contents: str):
        super().__init__(_dir_file_space_that_must_not_be_used_getter)
        self.contents = contents
        self._file_with_contents = fs.File('model-file.txt', self.contents)

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir = Path(tmp_dir_name)
            fs.DirContents([self._file_with_contents]).write_to(tmp_dir)

            yield sut.string_source_of_file__poorly_described(
                tmp_dir / self._file_with_contents.name,
                app_env.tmp_files_space,
            )

    def _string_source(self,
                       model_file: Path,
                       app_env: ApplicationEnvironment,
                       ) -> StringSource:
        raise NotImplementedError('abstract method')


class _SourceConstructorOfPoorlyDescribed(_SourceConstructorWSingleTmpFileBase):
    def _string_source(self,
                       model_file: Path,
                       app_env: ApplicationEnvironment,
                       ) -> StringSource:
        return sut.string_source_of_file__poorly_described(
            model_file,
            app_env.tmp_files_space,
        )


class _SourceConstructorOfExplicitlyDescribed(_SourceConstructorWSingleTmpFileBase):
    def _string_source(self,
                       model_file: Path,
                       app_env: ApplicationEnvironment,
                       ) -> StringSource:
        return sut.StringSourceOfFile(
            model_file,
            path_describer.PathDescriberForPrimitiveTestImpl('the description'),
            app_env.tmp_files_space,
        )


class _SourceConstructorOfDescribed(SourceConstructorWAppEnvForTest):
    def __init__(self, contents: str):
        super().__init__(_dir_file_space_that_must_not_be_used_getter)
        self.contents = contents
        file_with_contents = fs.File('model-file.txt', self.contents)
        relativity = RelOptionType.REL_TMP
        self._ddv = path_ddvs.simple_of_rel_option(relativity, file_with_contents.name)
        self._tcds_populator = tcds_populators.TcdsPopulatorForRelOptionType(
            relativity,
            fs.DirContents([file_with_contents])
        )

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        with ds_construction.tcds_with_act_as_curr_dir_2(tcds_contents=self._tcds_populator) as tcds:
            described_path = self._ddv.value_of_any_dependency__d(tcds)
            yield sut.string_source_of_file__described(
                described_path,
                app_env.tmp_files_space,
            )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
