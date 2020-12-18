import io
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from typing import TextIO, Sequence

from exactly_lib.util.file_utils import misc_utils
from exactly_lib.util.file_utils import spooled_file as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.programs.python_program_execution import \
    PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE
from exactly_lib_test.test_resources.recording import MaxNumberOfTimesChecker
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestUseAsMemBuff),
        TestMemBufferOverflowShouldCauseConversionToFileOnDisk(),
        TestAccessOfFileNoShouldCauseConversionToFileOnDisk(),
        TestCaptureOutputFromProcess(),
    ])


class TestUseAsMemBuff(unittest.TestCase):
    def test_open(self):
        mem_buff_size = 0
        expectation = is_open_mem_buff_with_contents(0, '', '')

        with sut.SpooledTextFile(mem_buff_size, _get_path__error_if_used) as f:
            expectation.apply_without_message(self, f)

        self.assertTrue(f.closed, 'closed')

    def test_write_to_mem(self):
        lines = [
            '1st\n',
            '2nd\n',
            '3rd\n',
        ]
        lines_as_str = ''.join(lines)
        mem_buff_size = len(lines_as_str)

        expectation = is_open_mem_buff_with_contents(len(lines_as_str), '', lines_as_str)

        with sut.SpooledTextFile(mem_buff_size, _get_path__error_if_used) as f:
            f.write(lines[0])
            f.writelines(lines[1:])
            expectation.apply_without_message(self, f)

        self.assertTrue(f.closed, 'closed')

    def test_write_to_mem__w_new_line(self):
        contents_w_std_new_line = 'contents\n'
        mem_buff_size = len(contents_w_std_new_line) * 2

        expectation = is_open_mem_buff_with_contents(len(contents_w_std_new_line), '', contents_w_std_new_line)

        with sut.SpooledTextFile(mem_buff_size, _get_path__error_if_used) as f:
            f.write(contents_w_std_new_line)
            expectation.apply_without_message(self, f)

        self.assertTrue(f.closed, 'closed')

    def test_write_to_mem_and_read(self):
        contents = '0123456789'
        seek_pos = 5
        mem_buff_size = len(contents)

        expectation_after_seek = is_open_mem_buff_with_contents(seek_pos,
                                                                contents[seek_pos:],
                                                                contents)

        with sut.SpooledTextFile(mem_buff_size, _get_path__error_if_used) as f:
            f.write(contents)
            f.seek(seek_pos, os.SEEK_SET)
            expectation_after_seek.apply_without_message(self, f)

        self.assertTrue(f.closed, 'closed')


class TestMemBufferOverflowShouldCauseConversionToFileOnDisk(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        buff_size = 10
        write_method_cases = [
            NameAndValue(
                'write',
                _write_to,
            ),
            NameAndValue(
                'writelines',
                _writelines_to,
            ),
        ]
        data_cases = [
            NameAndValue(
                'overflow on first write',
                ['x' * buff_size + 'y'],
            ),
            NameAndValue(
                'overflow on non-first write',
                ['x' * buff_size,
                 'y'],
            ),
            NameAndValue(
                'overflow on non-first write, followed by more write',
                ['x' * buff_size,
                 'y',
                 'after buffer overflow',
                 ],
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            path_sequence = _PathSequence(pathlib.Path(tmp_dir_name))
            for data_case in data_cases:
                all_data_written = ''.join(data_case.value)
                for write_method_case in write_method_cases:
                    generated_path = path_sequence.next()
                    path_getter = _GetSingleConstPath(self, generated_path)
                    with self.subTest(data_case=data_case.name,
                                      write_method_case=write_method_case.name):
                        # ACT #
                        with sut.SpooledTextFile(buff_size, path_getter.get_path) as f:
                            write_method_case.value(f, data_case.value)
                            # ASSERT #
                            is_file_on_disk_with_remaining_contents(
                                path_of_file_on_disk=asrt.equals(generated_path),
                                position=len(all_data_written),
                                remaining_contents='',
                            ).apply_without_message(self, f)
                            contents_from_start(
                                all_data_written
                            ).apply_without_message(self, f)

                        self.assertTrue(f.closed, 'closed')


class TestAccessOfFileNoShouldCauseConversionToFileOnDisk(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        chunk = '12345678'
        buff_size = 2 * len(chunk)
        data_cases = [
            NameAndValue(
                'empty file - no writes (mem buff)',
                [],
            ),
            NameAndValue(
                'single write (mem buff)',
                [chunk],
            ),
            NameAndValue(
                'multiple writes (mem buff)',
                [chunk, chunk],
            ),
            NameAndValue(
                'multiple writes (implicit conversion to file on disk)',
                [chunk, chunk, chunk],
            ),
        ]

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            path_sequence = _PathSequence(pathlib.Path(tmp_dir_name))
            for data_case in data_cases:
                all_data_written = ''.join(data_case.value)
                generated_path = path_sequence.next()
                path_getter = _GetSingleConstPath(self, generated_path)
                with self.subTest(data_case.name):
                    # ACT #
                    with sut.SpooledTextFile(buff_size, path_getter.get_path) as f:
                        _write_to(f, data_case.value)
                        fileno = f.fileno()
                        # ASSERT #
                        type_is_file_on_disk(
                            path_of_file_on_disk=asrt.equals(generated_path),
                            fileno=asrt.equals(fileno),
                        ).apply_without_message(self, f)
                        contents_from_start(
                            all_data_written
                        ).apply_without_message(self, f)

                    self.assertTrue(f.closed, 'closed')


class TestCaptureOutputFromProcess(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        copy_stdin_to_stdout_program = [
            sys.executable,
            PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
            py_programs.py_pgm_that_copies_stdin_to_stdout()
        ]

        stdin_contents = 'the contents of stdin'
        buff_size = len(stdin_contents) * 2
        with tmp_dir() as tmp_dir_path:
            stdin_path = tmp_dir_path / 'stdin'
            stdout_path = tmp_dir_path / 'stdout'
            stdin_path_getter = _GetSingleConstPath(self, stdin_path)
            stdout_path_getter = _GetSingleConstPath(self, stdout_path)
            # ACT #
            with sut.SpooledTextFile(buff_size, stdin_path_getter.get_path) as f_stdin:
                f_stdin.write(stdin_contents)
                _seek_to_start(f_stdin)
                with sut.SpooledTextFile(buff_size, stdout_path_getter.get_path) as f_stdout:
                    subprocess.run(args=copy_stdin_to_stdout_program,
                                   stdin=f_stdin,
                                   stdout=f_stdout,
                                   stderr=subprocess.DEVNULL)
            # ASSERT #
            contents_of_stdout_file = misc_utils.contents_of(stdout_path)
            self.assertEqual(stdin_contents,
                             contents_of_stdout_file)


def is_open() -> ValueAssertion[sut.SpooledTextFile]:
    return asrt.sub_component(
        'closed',
        sut.SpooledTextFile.closed.fget,
        asrt.equals(False),
    )


def is_at_pos_with_remaining_contents(position: int,
                                      remaining_contents: str,
                                      ) -> ValueAssertion[sut.SpooledTextFile]:
    return asrt.and_([
        asrt.sub_component(
            'tell',
            sut.SpooledTextFile.tell,
            asrt.equals(position),
        ),
        asrt.sub_component(
            'read (remaining contents)',
            sut.SpooledTextFile.read,
            asrt.equals(remaining_contents),
        ),
    ])


def contents_from_start(contents: str) -> ValueAssertion[sut.SpooledTextFile]:
    return asrt.and_([
        asrt.after_manipulation(
            _seek_to_start,
            asrt.sub_component(
                'contents, via read',
                _read_until_eof__via_read,
                asrt.equals(contents),
            ),
            'after seek to start',
        ),
        asrt.after_manipulation(
            _seek_to_start,
            asrt.sub_component(
                'contents, via readline',
                _read_until_eof__via_readline,
                asrt.equals(contents),
            ),
            'after seek to start',
        ),
        asrt.after_manipulation(
            _seek_to_start,
            asrt.sub_component(
                'contents, via readlines',
                _read_until_eof__via_readlines,
                asrt.equals(contents),
            ),
            'after seek to start',
        ),
        asrt.after_manipulation(
            _seek_to_start,
            asrt.sub_component(
                'contents, via readlines as context manager',
                _read_until_eof__via_readlines_ctx_mgr,
                asrt.equals(contents),
            ),
            'after seek to start',
        ),
    ])


def _seek_to_start(f: sut.SpooledTextFile):
    f.seek(0, io.SEEK_SET)


def _read_until_eof__via_read(f: sut.SpooledTextFile) -> str:
    return f.read()


def _read_until_eof__via_readline(f: sut.SpooledTextFile) -> str:
    lines = []
    while True:
        s = f.readline()
        if s == '':
            return ''.join(lines)
        else:
            lines.append(s)


def _read_until_eof__via_readlines(f: sut.SpooledTextFile) -> str:
    return ''.join(f.readlines())


def _read_until_eof__via_readlines_ctx_mgr(f: sut.SpooledTextFile) -> str:
    with f as lines:
        return ''.join(lines)


def type_is_mem_buff() -> ValueAssertion[sut.SpooledTextFile]:
    return asrt.and_([
        asrt.sub_component(
            'is_mem_buff',
            sut.SpooledTextFile.is_mem_buff.fget,
            asrt.equals(True),
        ),
        asrt.sub_component(
            'is_file_on_disk',
            sut.SpooledTextFile.is_file_on_disk.fget,
            asrt.equals(False),
        ),
    ])


def type_is_file_on_disk(path_of_file_on_disk: ValueAssertion[pathlib.Path],
                         fileno: ValueAssertion[int] = asrt.anything_goes(),
                         ) -> ValueAssertion[sut.SpooledTextFile]:
    return asrt.and_([
        asrt.sub_component(
            'is_mem_buff',
            sut.SpooledTextFile.is_mem_buff.fget,
            asrt.equals(False),
        ),
        asrt.sub_component(
            'is_file_on_disk',
            sut.SpooledTextFile.is_file_on_disk.fget,
            asrt.equals(True),
        ),
        asrt.sub_component(
            'fileno',
            sut.SpooledTextFile.fileno,
            asrt.is_instance_with(int, fileno),
        ),
        asrt.sub_component(
            'path_of_file_on_disk',
            sut.SpooledTextFile.path_of_file_on_disk.fget,
            path_of_file_on_disk,
        ),
    ])


def is_open_mem_buff_with_contents(position: int,
                                   remaining_contents: str,
                                   full_contents: str) -> ValueAssertion[sut.SpooledTextFile]:
    return asrt.and_([
        is_open(),
        type_is_mem_buff(),
        asrt.sub_component(
            'mem_buff',
            sut.SpooledTextFile.mem_buff.fget,
            asrt.equals(full_contents),
        ),
        is_at_pos_with_remaining_contents(position,
                                          remaining_contents),
    ])


def is_file_on_disk_with_remaining_contents(path_of_file_on_disk: ValueAssertion[pathlib.Path],
                                            position: int,
                                            remaining_contents: str,
                                            ) -> ValueAssertion[sut.SpooledTextFile]:
    return asrt.and_([
        is_open(),
        type_is_file_on_disk(path_of_file_on_disk),
        is_at_pos_with_remaining_contents(position,
                                          remaining_contents),
    ])


def _get_path__error_if_used() -> pathlib.Path:
    raise ValueError('should not be used')


def _write_to(f: TextIO, data: Sequence[str]):
    for data in data:
        f.write(data)


def _writelines_to(f: TextIO, data: Sequence[str]):
    f.writelines(data)


class _GetSingleConstPath:
    def __init__(self,
                 put: unittest.TestCase,
                 path: pathlib.Path,
                 ):
        self._invocations_counter = MaxNumberOfTimesChecker(put, 1, 'path getter')
        self._path = path

    def get_path(self) -> pathlib.Path:
        self._invocations_counter.register()
        return self._path


class _PathSequence:
    def __init__(self, directory: pathlib.Path):
        self.directory = directory
        self.next_num = 0

    def next(self) -> pathlib.Path:
        self.next_num += 1
        return self.directory / str(self.next_num)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
