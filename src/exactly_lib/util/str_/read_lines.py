from typing import Iterator, Tuple


def read_lines_as_str__w_minimum_num_chars(min_num_chars_to_read: int, lines: Iterator[str]) -> Tuple[str, bool]:
    """
    :param min_num_chars_to_read >= 1
    :return: string read, source-may-have-more-contents
    """
    actual_read = 0
    actual_lines = []
    for line in lines:
        actual_lines.append(line)
        actual_read += len(line)
        if actual_read >= min_num_chars_to_read:
            break
    contents = ''.join(actual_lines)
    return contents, len(contents) >= min_num_chars_to_read
