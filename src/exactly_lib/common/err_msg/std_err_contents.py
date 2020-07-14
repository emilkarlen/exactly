from typing import TextIO

from exactly_lib.util.process_execution.exe_store_and_read_stderr import TextFromFileReader


class InitialPartReaderWithRestIndicator(TextFromFileReader):
    def __init__(self, limit: int):
        self._limit = limit

    def read(self, f: TextIO) -> str:
        chunk = f.read(self._limit)
        return (
            chunk
            if len(f.read(1)) == 0
            else
            chunk + '...'
        )


STD_ERR_TEXT_READER = InitialPartReaderWithRestIndicator(1024)
