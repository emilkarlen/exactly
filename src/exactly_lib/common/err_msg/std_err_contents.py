from typing import TextIO

from exactly_lib.util.file_utils.text_reader import TextFromFileReader


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
