import os
import unittest
from contextlib import contextmanager
from typing import ContextManager, IO

from exactly_lib.impls.types.string_source import cached_frozen as sut
from exactly_lib.impls.types.string_source.contents import contents_of_str
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.string_source.test_resources.dir_file_space_getter import \
    dir_file_space_for_single_usage_getter
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import \
    SourceConstructorWAppEnvForTest


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestUnfrozenThatDoNotUseFileNo),
        unittest.makeSuite(TestUnfrozenThatWritesToFileNo),
    ])


class TestUnfrozenThatDoNotUseFileNo(unittest.TestCase):
    def test_contents_is_smaller_than_mem_buff(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'empty',
                '',
            ),
            NameAndValue(
                'single line',
                'abc',
            ),
            NameAndValue(
                'multi line',
                '1st\n2nd\n',
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source_constructor = _SourceConstructorOfUnfrozenAsConstStr(case.value, 1 + len(case.value))
                expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                    ''.join(source_constructor.contents),
                    may_depend_on_external_resources=asrt.equals(False),
                    frozen_may_depend_on_external_resources=asrt.equals(False),
                )

                assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor),
                )

    def test_contents_is_larger_than_mem_buff(self):
        # ARRANGE #
        mem_buff_size = 4
        cases = [
            NameAndValue(
                'single line',
                'abc' * mem_buff_size,
            ),
            NameAndValue(
                'multi line',
                '1st\n2nd\n' * mem_buff_size,
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source_constructor = _SourceConstructorOfUnfrozenAsConstStr(case.value, mem_buff_size)
                expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                    ''.join(source_constructor.contents),
                    may_depend_on_external_resources=asrt.equals(False),
                    frozen_may_depend_on_external_resources=asrt.equals(True),
                )

                assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor),
                )


class TestUnfrozenThatWritesToFileNo(unittest.TestCase):
    def test_contents_is_smaller_than_mem_buff(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'single line',
                'abc',
            ),
            NameAndValue(
                'multi line',
                '1st\n2nd\n',
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source_constructor = _SourceConstructorOfUnfrozenThatWritesViaFileNo(case.value, 1 + len(case.value))
                expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                    ''.join(source_constructor.contents),
                    may_depend_on_external_resources=asrt.equals(False),
                    frozen_may_depend_on_external_resources=asrt.equals(False),
                )

                assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor),
                )

    def test_contents_is_larger_than_mem_buff(self):
        # ARRANGE #
        mem_buff_size = 4
        cases = [
            NameAndValue(
                'single line',
                'abc' * mem_buff_size,
            ),
            NameAndValue(
                'multi line',
                '1st\n2nd\n' * mem_buff_size,
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source_constructor = _SourceConstructorOfUnfrozenThatWritesViaFileNo(case.value, mem_buff_size)
                expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                    ''.join(source_constructor.contents),
                    may_depend_on_external_resources=asrt.equals(False),
                    frozen_may_depend_on_external_resources=asrt.equals(True),
                )

                assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor),
                )


class _SourceConstructorOfUnfrozenAsConstStr(SourceConstructorWAppEnvForTest):
    def __init__(self, contents: str, mem_buff_size: int):
        super().__init__(dir_file_space_for_single_usage_getter)
        self.contents = contents
        self.mem_buff_size = mem_buff_size

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        yield sut.StringSourceWithCachedFrozen(
            _new_structure_builder,
            contents_of_str.ContentsOfStr(
                self.contents,
                None,
                app_env.tmp_files_space,
            ),
            self.mem_buff_size,
            name_suffix=None,
        )


class _SourceConstructorOfUnfrozenThatWritesViaFileNo(SourceConstructorWAppEnvForTest):
    def __init__(self, contents: str, mem_buff_size: int):
        super().__init__(dir_file_space_for_single_usage_getter)
        self.contents = contents
        self.mem_buff_size = mem_buff_size

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        yield sut.StringSourceWithCachedFrozen(
            _new_structure_builder,
            _ContentsThatAccessesFileNo(
                self.contents,
                app_env.tmp_files_space,
            ),
            self.mem_buff_size,
            name_suffix=None,
        )


class _ContentsThatAccessesFileNo(contents_of_str.ContentsOfStr):
    def __init__(self,
                 contents: str,
                 tmp_file_space: DirFileSpace,
                 ):
        super().__init__(contents, 'file-name', tmp_file_space)

    def write_to(self, output: IO):
        file_no = output.fileno()
        super().write_to(output)
        output.flush()
        os.fsync(file_no)


def _new_structure_builder() -> StringSourceStructureBuilder:
    return StringSourceStructureBuilder('header', (), ())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
