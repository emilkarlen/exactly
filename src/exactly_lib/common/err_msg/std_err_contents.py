from typing import TextIO, List

from exactly_lib.util.file_utils.text_reader import TextFromFileReader


class InitialPartReaderWithRestIndicator(TextFromFileReader):
    REST_INDICATOR = '...'

    def __init__(self,
                 max_num_lines: int,
                 max_num_chars: int,
                 ):
        self._max_num_lines = max_num_lines
        self._max_num_chars = max_num_chars

    def read(self, f: TextIO) -> str:
        lines = self._read_lines(f)

        has_more_contents = (f.read(1) != '')

        if has_more_contents:
            lines.append(self.REST_INDICATOR)

        return ''.join(lines)

    def _read_lines(self, f: TextIO) -> List[str]:
        num_lines_left = self._max_num_lines
        num_chars_left = self._max_num_chars
        ret_val = []

        while num_chars_left > 0 and num_lines_left > 0:
            next_line = f.readline(num_chars_left)
            ret_val.append(next_line)

            num_chars_left -= len(next_line)
            num_lines_left -= 1

        return ret_val


STD_ERR_TEXT_READER = InitialPartReaderWithRestIndicator(32, 1024)
