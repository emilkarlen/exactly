import enum
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, Sequence, List, IO, Callable

from exactly_lib.impls.types.string_source.source_from_lines import StringSourceFromLinesBase
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib_test.common.test_resources import text_doc_assertions
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.actions import do_raise
from exactly_lib_test.test_resources.recording import SequenceRecorder
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_base import StringSourceTestImplBase


def string_source_that_must_not_be_used() -> StringSource:
    return StringSourceThat.new_w_defaults_of_not_impl()


class StringSourceThatRaisesHardErrorException(StringSourceTestImplBase):
    def __init__(self,
                 err_msg='hard error message',
                 may_depend_on_external_resources: bool = False,
                 ):
        self._err_msg = err_msg
        self._may_depend_on_external_resources = may_depend_on_external_resources

    def freeze(self):
        pass

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        raise ValueError('unsupported')

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._may_depend_on_external_resources

    @property
    def as_str(self) -> str:
        return self._raise_hard_error()

    @property
    def as_file(self) -> Path:
        return self._raise_hard_error()

    @property
    def as_lines(self) -> ContextManager[Iterator[str]]:
        return self._raise_hard_error()

    def write_to(self, output: IO):
        self._raise_hard_error()

    def _raise_hard_error(self):
        raise HardErrorException(
            text_doc_assertions.new_single_string_text_for_test(self._err_msg)
        )


class StringSourceDataHandler:
    def __init__(self,
                 may_depend_on_external_resources: Callable[[], bool],
                 as_str: Callable[[], str],
                 as_lines: Callable[[], Iterator[str]],
                 as_file: Callable[[DirFileSpace], Path],
                 write_to: Callable[[IO], None],
                 ):
        self.may_depend_on_external_resources = may_depend_on_external_resources
        self.as_str = as_str
        self.as_lines = as_lines
        self.as_file = as_file
        self.write_to = write_to

    @staticmethod
    def new_w_defaults_of_not_impl(
            may_depend_on_external_resources: Callable[[], bool] = do_raise(ValueError('should not be called')),
            as_str: Callable[[], str] = do_raise(ValueError('should not be called')),
            as_lines: Callable[[], Iterator[str]] = do_raise(ValueError('should not be called')),
            as_file: Callable[[DirFileSpace], Path] = do_raise(ValueError('should not be called')),
            write_to: Callable[[IO], None] = do_raise(ValueError('should not be called')),
    ) -> 'StringSourceDataHandler':
        return StringSourceDataHandler(
            may_depend_on_external_resources=may_depend_on_external_resources,
            as_str=as_str,
            as_lines=as_lines,
            as_file=as_file,
            write_to=write_to,
        )

    @staticmethod
    def new_w_defaults_of_hard_error(
            may_depend_on_external_resources: bool,
            as_str: Callable[[], str]
            = do_raise(HardErrorException(asrt_text_doc.new_single_string_text_for_test('should not be called'))),
            as_lines: Callable[[], Iterator[str]]
            = do_raise(HardErrorException(asrt_text_doc.new_single_string_text_for_test('should not be called'))),
            as_file: Callable[[DirFileSpace], Path]
            = do_raise(HardErrorException(asrt_text_doc.new_single_string_text_for_test('should not be called'))),
            write_to: Callable[[IO], None]
            = do_raise(HardErrorException(asrt_text_doc.new_single_string_text_for_test('should not be called'))),

    ) -> 'StringSourceDataHandler':
        def _may_depend_on_external_resources() -> bool:
            return may_depend_on_external_resources

        return StringSourceDataHandler(
            may_depend_on_external_resources=_may_depend_on_external_resources,
            as_str=as_str,
            as_lines=as_lines,
            as_file=as_file,
            write_to=write_to,
        )

    @staticmethod
    def of_constants(contents: str,
                     may_depend_on_external_resources: bool,
                     ) -> 'StringSourceDataHandler':
        def _may_depend_on_external_resources() -> bool:
            return may_depend_on_external_resources

        return StringSourceDataHandler.of_constants_2(
            contents,
            _may_depend_on_external_resources,
        )

    @staticmethod
    def of_constants_2(contents: str,
                       may_depend_on_external_resources: Callable[[], bool],
                       ) -> 'StringSourceDataHandler':
        def as_str() -> str:
            return contents

        def as_lines() -> Iterator[str]:
            return iter(contents.splitlines(keepends=True))

        def as_file(tmp_file_space: DirFileSpace) -> Path:
            ret_val = tmp_file_space.new_path('data-handler.txt')
            with ret_val.open('w') as f:
                f.write(contents)
            return ret_val

        def write_to(output: IO):
            output.write(contents)

        return StringSourceDataHandler(
            may_depend_on_external_resources=may_depend_on_external_resources,
            as_str=as_str,
            as_lines=as_lines,
            as_file=as_file,
            write_to=write_to,
        )


class StringSourceOfDataHandlers(StringSourceTestImplBase):
    def __init__(self,
                 tmp_file_space: Callable[[], DirFileSpace],
                 before_freeze: StringSourceDataHandler,
                 after_freeze: StringSourceDataHandler,
                 ):
        self.__tmp_file_space = tmp_file_space
        self._data = before_freeze
        self._after_freeze = after_freeze

    def freeze(self):
        self._data = self._after_freeze

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._data.may_depend_on_external_resources()

    @property
    def as_file(self) -> Path:
        return self._data.as_file(self._tmp_file_space)

    @property
    def as_str(self) -> str:
        return self._data.as_str()

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield self._data.as_lines()

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space()


class StringSourceThat(StringSourceTestImplBase):
    def __init__(self,
                 tmp_file_space: Callable[[], DirFileSpace],
                 may_depend_on_external_resources: Callable[[], bool],
                 as_str: Callable[[], str],
                 as_lines: Callable[[], Iterator[str]],
                 as_file: Callable[[], Path],
                 write_to: Callable[[IO], None],
                 ):
        self.__tmp_file_space = tmp_file_space
        self._may_depend_on_external_resources = may_depend_on_external_resources
        self._as_str = as_str
        self._as_lines = as_lines
        self._as_file = as_file
        self._write_to = write_to

    @staticmethod
    def new_w_defaults_of_not_impl(
            tmp_file_space: Callable[[], DirFileSpace] = do_raise(ValueError('should not be called')),
            may_depend_on_external_resources: Callable[[], bool] = do_raise(ValueError('should not be called')),
            as_str: Callable[[], str] = do_raise(ValueError('should not be called')),
            as_lines: Callable[[], Iterator[str]] = do_raise(ValueError('should not be called')),
            as_file: Callable[[], Path] = do_raise(ValueError('should not be called')),
            write_to: Callable[[IO], None] = do_raise(ValueError('should not be called')),
    ) -> StringSource:
        return StringSourceThat(
            tmp_file_space=tmp_file_space,
            may_depend_on_external_resources=may_depend_on_external_resources,
            as_str=as_str,
            as_lines=as_lines,
            as_file=as_file,
            write_to=write_to,
        )

    def freeze(self):
        pass

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space()

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._may_depend_on_external_resources()

    @property
    def as_str(self) -> str:
        return self._as_str()

    @property
    def as_file(self) -> Path:
        return self._as_file()

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield self._as_lines()

    def write_to(self, output: IO):
        self._write_to(output)


class StringSourceFromLines(StringSourceFromLinesBase, StringSourceTestImplBase):
    def __init__(self,
                 lines: Sequence[str],
                 tmp_file_space: DirFileSpace,
                 may_depend_on_external_resources: bool = False,
                 ):
        super().__init__()
        self._lines = lines
        self._may_depend_on_external_resources = may_depend_on_external_resources
        self.__tmp_file_space = tmp_file_space

    def freeze(self):
        pass

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._may_depend_on_external_resources

    @property
    def as_str(self) -> str:
        return ''.join(self._lines)

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter(self._lines)


def of_lines__w_check_for_validity(
        put: unittest.TestCase,
        lines: Sequence[str],
        tmp_file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
        may_depend_on_external_resources: bool = False,
) -> StringSource:
    ret_val = StringSourceFromLines(lines,
                                    tmp_file_space,
                                    may_depend_on_external_resources)
    asrt_string_source.StringSourceLinesAreValidAssertion().apply_with_message(
        put,
        ret_val,
        'model lines validity'
    )
    return ret_val


def of_string(
        contents: str,
        tmp_file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
        may_depend_on_external_resources: bool = False,
) -> StringSource:
    return StringSourceFromLines(
        contents.splitlines(keepends=True),
        tmp_file_space,
        may_depend_on_external_resources,
    )


def as_lines_list__w_lines_validation(put: unittest.TestCase,
                                      model: StringSource,
                                      ) -> List[str]:
    checker_source = asrt_string_source.StringSourceThatThatChecksLines(put, model)
    with checker_source.as_lines as lines:
        return list(lines)


class DelegatingStringSource(StringSource):
    def __init__(self, target: StringSource):
        self._target = target

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._target.new_structure_builder()

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._target.may_depend_on_external_resources

    def freeze(self):
        self._target.freeze()

    @property
    def as_lines(self) -> ContextManager[Iterator[str]]:
        return self._target.as_lines

    @property
    def as_str(self) -> str:
        return self._target.as_str

    @property
    def as_file(self) -> Path:
        return self._target.as_file

    def write_to(self, output: IO):
        self._target.write_to(output)

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self._target._tmp_file_space


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
