import unittest
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, Sequence, TextIO

from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources import test_of_test_resources_util as test_utils
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, MessageBuilder
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions as sut, \
    source_constructors
from exactly_lib_test.type_val_prims.string_source.test_resources.multi_obj_assertions import SourceConstructor
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import \
    SourceConstructorWAppEnvForTest, DirFileSpaceGetter
from exactly_lib_test.type_val_prims.string_source.test_resources.string_sources import StringSourceOfContents


class StringSourceData:
    def __init__(self,
                 contents: str = '',
                 may_depend_on_external_resources: bool = False,
                 ):
        self.data__as_str = contents
        self.data__as_lines = as_line_sequence(contents)
        self.data__as_file = contents
        self.data__write_to = contents
        self.may_depend_on_external_resources = may_depend_on_external_resources


def _string_source_of_contents_data(before_freeze: StringSourceData,
                                    after_freeze: StringSourceData,
                                    tmp_file_space: DirFileSpace,
                                    ) -> StringSource:
    return StringSourceOfContents(
        _ContentsOfContentsData(before_freeze, tmp_file_space),
        _ContentsOfContentsData(after_freeze, tmp_file_space),
    )


class _ContentsOfContentsData(StringSourceContents):
    def __init__(self,
                 data: StringSourceData,
                 tmp_file_space: DirFileSpace,
                 ):
        self._data = data
        self._tmp_file_space = tmp_file_space

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._tmp_file_space

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._data.may_depend_on_external_resources

    @property
    def as_str(self) -> str:
        return self._data.data__as_str

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self._data.data__as_lines)

    def write_to(self, output: TextIO):
        output.write(self._data.data__write_to)

    @property
    def as_file(self) -> Path:
        ret_val = self._tmp_file_space.new_path('as-file')
        with ret_val.open('w') as f:
            f.write(self._data.data__as_file)
        return ret_val


class ConstructorOfStringSourceData(SourceConstructorWAppEnvForTest):
    def __init__(self,
                 before_freeze: StringSourceData,
                 after_freeze: StringSourceData,
                 get_dir_file_space: DirFileSpaceGetter
                 = source_constructors.get_dir_file_space_with_existing_dir,
                 ):
        super().__init__(get_dir_file_space)
        self.before_freeze = before_freeze
        self.after_freeze = after_freeze

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        yield _string_source_of_contents_data(self.before_freeze,
                                              self.after_freeze,
                                              app_env.tmp_files_space)


def as_line_sequence(s: str) -> Sequence[str]:
    return s.splitlines(keepends=True)


def check_variants(expectation: sut.ExpectationOnUnFrozenAndFrozen,
                   ) -> Sequence[NameAndValue[Assertion[sut.SourceConstructors]]]:
    return [
        NameAndValue(
            'check sequence permutations',
            sut.assertion_of_sequence_permutations(expectation),
        ),
        NameAndValue(
            'check_with_first_access_is_not_write_to',
            sut.assertion_of_first_access_is_not_write_to(expectation),
        ),
        NameAndValue(
            'check_2_seq_w_file_first_and_last',
            sut.assertion_of_2_seq_w_file_first_and_last(expectation),
        ),
    ]


class TestUnexpectedDataBase(unittest.TestCase, ABC):
    def runTest(self):
        # ARRANGE #
        may_depend_on_external_resources = False
        expected = 'the expected contents'
        expectation = sut.ExpectationOnUnFrozenAndFrozen.equals(
            expected,
            may_depend_on_external_resources=asrt.equals(may_depend_on_external_resources),
            frozen_may_depend_on_external_resources=asrt.equals(may_depend_on_external_resources),
        )

        data__expected = StringSourceData(expected, may_depend_on_external_resources)

        data__external_dependencies = StringSourceData(expected, not may_depend_on_external_resources)

        data__as_str = StringSourceData(expected, may_depend_on_external_resources)
        data__as_str.data__as_str = 'different contents of as_str'

        data__as_lines = StringSourceData(expected, may_depend_on_external_resources)
        data__as_lines.data__as_lines = as_line_sequence('different contents of as_lines')

        data__as_file = StringSourceData(expected, may_depend_on_external_resources)
        data__as_file.data__as_file = 'different contents of as_file'

        data__write_to = StringSourceData(expected, may_depend_on_external_resources)
        data__write_to.data__write_to = 'different contents of write_to'

        contents_cases = [
            NameAndValue(
                'may_depend_on_external_resources differ',
                data__external_dependencies,
            ),
            NameAndValue(
                'as_str differ',
                data__as_str,
            ),
            NameAndValue(
                'as_lines differ',
                data__as_lines,
            ),
            NameAndValue(
                'as_file differ',
                data__as_file,
            ),
            NameAndValue(
                'write_to differ',
                data__write_to,
            ),
        ]
        for contents_case in contents_cases:
            source_constructor = self._source_constructor(data__expected, contents_case.value)
            for check_variant in check_variants(expectation):
                with self.subTest(data_case=contents_case.name, check_method=check_variant.name):
                    # ACT & ASSERT #
                    test_utils.assert_that_assertion_fails(
                        check_variant.value,
                        sut.SourceConstructors.of_common(source_constructor),
                    )

    @abstractmethod
    def _source_constructor(self,
                            expected: StringSourceData,
                            unexpected: StringSourceData,
                            ) -> SourceConstructor:
        raise NotImplementedError('abstract method')


class TestInvalidLineSequenceIsDetectedBase(unittest.TestCase, ABC):
    def runTest(self):
        # ARRANGE #
        may_depend_on_external_resources = False
        expected = 'the expected\ncontents'
        expected__invalid_line_sequence = ('the expected', '\ncontents')

        expectation = sut.ExpectationOnUnFrozenAndFrozen.equals(
            expected,
            may_depend_on_external_resources=asrt.equals(may_depend_on_external_resources),
            frozen_may_depend_on_external_resources=asrt.equals(may_depend_on_external_resources),
        )

        data__valid = StringSourceData(expected, may_depend_on_external_resources)

        data__invalid_line_sequence = StringSourceData(expected, may_depend_on_external_resources)
        data__invalid_line_sequence.data__as_lines = expected__invalid_line_sequence

        source_constructor = self._source_constructor(data__valid, data__invalid_line_sequence)
        for check_variant in check_variants(expectation):
            with self.subTest(check_method=check_variant.name):
                # ACT & ASSERT #
                test_utils.assert_that_assertion_fails(
                    check_variant.value,
                    sut.SourceConstructors.of_common(source_constructor),
                )

    @abstractmethod
    def _source_constructor(self,
                            valid: StringSourceData,
                            invalid: StringSourceData,
                            ) -> SourceConstructor:
        raise NotImplementedError('abstract method')
