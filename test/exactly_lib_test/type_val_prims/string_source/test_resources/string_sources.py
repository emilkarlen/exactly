import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, Sequence, List, IO, Callable

from exactly_lib.impls.types.string_source.source_from_lines import StringSourceFromLinesBase
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib_test.common.test_resources import text_doc_assertions
from exactly_lib_test.test_resources.actions import do_raise
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_base import StringSourceTestImplBase


def string_source_that_must_not_be_used() -> StringSource:
    return StringSourceThat.new_w_defaults_of_not_impl()


class StringSourceThatRaisesHardErrorException(StringSourceTestImplBase):
    def __init__(self, err_msg='hard error message'):
        self._err_msg = err_msg

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        raise ValueError('unsupported')

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._raise_hard_error()

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
