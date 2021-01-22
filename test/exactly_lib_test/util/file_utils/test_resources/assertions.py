import unittest
from typing import Union, IO

from exactly_lib.util.file_utils.std import ProcessExecutionFile
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, MessageBuilder


class IsProcessExecutionFileWIthContents(ValueAssertionBase[ProcessExecutionFile]):
    def __init__(self, expected: str):
        self._expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value: ProcessExecutionFile,
               message_builder: MessageBuilder,
               ):
        put.assertIsNotNone(
            value,
            message_builder.apply('file value'),
        )
        if isinstance(value, int):
            put.assertGreaterEqual(
                value,
                0,
                message_builder.apply('file integer value'),
            )
        actual_contents = self._contents(value)
        put.assertEqual(
            self._expected,
            actual_contents,
            message_builder.apply('file contents')
        )

    def _contents(self, open_file: Union[int, IO]) -> str:
        file = self._io_file(open_file)
        return file.read()

    @staticmethod
    def _io_file(open_file: Union[int, IO]) -> IO:
        return (
            open(open_file, closefd=False)
            if isinstance(open_file, int)
            else
            open_file
        )
