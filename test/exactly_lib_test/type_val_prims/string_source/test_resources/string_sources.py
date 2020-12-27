import enum
import unittest
from pathlib import Path
from typing import ContextManager, Iterator, Sequence, List, IO

from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib_test.test_resources.recording import SequenceRecorder
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source, \
    contents_assertions as asrt_str_src_contents
from exactly_lib_test.type_val_prims.string_source.test_resources import string_source_contents
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_base import StringSourceTestImplBase
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_contents import \
    StringSourceContentsFromLines, DelegatingStringSourceContents


def string_source_that_must_not_be_used() -> StringSource:
    return StringSourceOfContents.of_identical(
        string_source_contents.StringSourceContentsThat.new_w_defaults_of_not_impl()
    )


def string_source_that_raises_hard_error_exception(err_msg='hard error message',
                                                   may_depend_on_external_resources: bool = False,
                                                   ) -> StringSource:
    return StringSourceOfContents.of_identical(
        string_source_contents.ContentsThatRaisesHardErrorException(err_msg, may_depend_on_external_resources)
    )


class StringSourceOfContents(StringSourceTestImplBase):
    def __init__(self,
                 before_freeze: StringSourceContents,
                 after_freeze: StringSourceContents,
                 ):
        self._contents = before_freeze
        self._after_freeze = after_freeze

    @staticmethod
    def of_identical(before_and_after_freeze: StringSourceContents) -> StringSource:
        return StringSourceOfContents(before_and_after_freeze,
                                      before_and_after_freeze)

    def freeze(self):
        self._contents = self._after_freeze

    def contents(self) -> StringSourceContents:
        return self._contents


def string_source_from_lines(lines: Sequence[str],
                             tmp_file_space: DirFileSpace,
                             may_depend_on_external_resources: bool = False,
                             ) -> StringSource:
    return StringSourceOfContents.of_identical(
        StringSourceContentsFromLines(
            lines,
            tmp_file_space,
            may_depend_on_external_resources
        ),
    )


def new_structure_builder() -> StringSourceStructureBuilder:
    return StringSourceStructureBuilder('test resources impl', (), ())


def of_lines__w_check_for_validity(
        put: unittest.TestCase,
        lines: Sequence[str],
        tmp_file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
        may_depend_on_external_resources: bool = False,
) -> StringSource:
    ret_val = string_source_from_lines(lines,
                                       tmp_file_space,
                                       may_depend_on_external_resources)
    asrt_str_src_contents.StringSourceContentsLinesAreValidAssertion().apply_with_message(
        put,
        ret_val.contents(),
        'model lines validity'
    )
    return ret_val


def of_string(
        contents: str,
        tmp_file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
        may_depend_on_external_resources: bool = False,
) -> StringSource:
    return string_source_from_lines(
        contents.splitlines(keepends=True),
        tmp_file_space,
        may_depend_on_external_resources,
    )


def as_lines_list__w_lines_validation(put: unittest.TestCase,
                                      model: StringSource,
                                      ) -> List[str]:
    checker_source = asrt_string_source.StringSourceThatThatChecksLines(put, model)
    with checker_source.contents().as_lines as lines:
        return list(lines)


class DelegatingStringSource(StringSource):
    def __init__(self, target: StringSource):
        self._target = target

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._target.new_structure_builder()

    def freeze(self):
        self._target.freeze()

    def contents(self) -> StringSourceContents:
        return self._target.contents()


class StringSourceMethod(enum.IntEnum):
    MAY_DEPEND_ON_EXTERNAL_RESOURCES = 1
    FREEZE = 2
    AS_LINES = 3
    AS_STR = 4
    AS_FILE = 5
    WRITE_TO = 6


class StringSourceThatRecordsMethodInvocations(DelegatingStringSource):
    def __init__(self,
                 checked: StringSource,
                 method_invocation_recorder: SequenceRecorder[StringSourceMethod],
                 ):
        super().__init__(checked)
        self.method_invocation_recorder = method_invocation_recorder

    def freeze(self):
        self.method_invocation_recorder.record(StringSourceMethod.FREEZE)
        super().freeze()

    def contents(self) -> StringSourceContents:
        return StringSourceContentsThatRecordsMethodInvocations(self._target.contents(),
                                                                self.method_invocation_recorder)


class StringSourceContentsThatRecordsMethodInvocations(DelegatingStringSourceContents):
    def __init__(self,
                 checked: StringSourceContents,
                 method_invocation_recorder: SequenceRecorder[StringSourceMethod],
                 ):
        super().__init__(checked)
        self.method_invocation_recorder = method_invocation_recorder

    @property
    def may_depend_on_external_resources(self) -> bool:
        self.method_invocation_recorder.record(StringSourceMethod.MAY_DEPEND_ON_EXTERNAL_RESOURCES)
        return super().may_depend_on_external_resources

    @property
    def as_lines(self) -> ContextManager[Iterator[str]]:
        self.method_invocation_recorder.record(StringSourceMethod.AS_LINES)
        return super().as_lines

    @property
    def as_str(self) -> str:
        self.method_invocation_recorder.record(StringSourceMethod.AS_STR)
        return super().as_str

    @property
    def as_file(self) -> Path:
        self.method_invocation_recorder.record(StringSourceMethod.AS_FILE)
        return super().as_file

    def write_to(self, output: IO):
        self.method_invocation_recorder.record(StringSourceMethod.WRITE_TO)
        super().write_to(output)
