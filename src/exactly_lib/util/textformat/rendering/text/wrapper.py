from contextlib import contextmanager
from textwrap import TextWrapper
from typing import List


class Indent(tuple):
    def __new__(cls,
                first_line: str,
                following_lines: str):
        return tuple.__new__(cls, (first_line, following_lines))

    @staticmethod
    def identical(indent: str) -> 'Indent':
        """
        :return: Indent is identical for the first line
        and following lines.
        """
        return Indent(indent, indent)

    @property
    def first_line(self) -> str:
        return self[0]

    @property
    def following_lines(self) -> str:
        return self[1]


class Wrapper:
    def __init__(self,
                 page_width: int = 70):
        self.text_wrapper = TextWrapper(width=page_width)
        self._saved_indents_stack = []

    def wrap(self, text: str) -> list:
        return self.text_wrapper.wrap(text)

    def no_word_wrap(self, lines: list) -> List[str]:
        """
        Outputs lines without wrapping.
        Each line will begin on a new line.
        :param lines: List of text that does not contain
        new-line characters.
        """
        if not lines:
            return []
        ret_val = []
        line = lines[0]
        rest = lines[1:]
        window_width = self.page_width - len(self.text_wrapper.initial_indent)
        output_line = self._get_first_output_line_and_store_remaining_part(window_width,
                                                                           line,
                                                                           rest)
        ret_val.append(self.text_wrapper.initial_indent + output_line)
        window_width = self.page_width - len(self.text_wrapper.subsequent_indent)
        while rest:
            line = rest.pop(0)
            output_line = self._get_first_output_line_and_store_remaining_part(window_width,
                                                                               line,
                                                                               rest)
            ret_val.append(self.text_wrapper.subsequent_indent + output_line)
        return ret_val

    @staticmethod
    def _get_first_output_line_and_store_remaining_part(window_width: int,
                                                        line: str,
                                                        remaining_lines: list) -> str:
        if window_width <= 0:
            return line
        else:
            ret_val = line[:window_width]
            rest_of_first_line = line[window_width:]
            if rest_of_first_line:
                remaining_lines.insert(0, rest_of_first_line)
            return ret_val

    @staticmethod
    def blank_lines(num_lines=1) -> List[str]:
        return num_lines * ['']

    @property
    def page_width(self) -> int:
        return self.text_wrapper.width

    @property
    def current_indent(self) -> Indent:
        return Indent(self.text_wrapper.initial_indent,
                      self.text_wrapper.subsequent_indent)

    @property
    def saved_indents_stack(self) -> List[Indent]:
        return self._saved_indents_stack

    def push_indent(self, indent: Indent):
        text_wrapper = self.text_wrapper
        self._saved_indents_stack.insert(0, self.current_indent)
        text_wrapper.initial_indent = indent.first_line
        text_wrapper.subsequent_indent = indent.following_lines

    def push_indent_increase(self, delta: Indent):
        text_wrapper = self.text_wrapper
        indent = Indent(text_wrapper.initial_indent + delta.first_line,
                        text_wrapper.subsequent_indent + delta.following_lines)
        self.push_indent(indent)

    def pop_indent(self):
        indent = self._saved_indents_stack.pop(0)
        self.text_wrapper.initial_indent = indent.first_line
        self.text_wrapper.subsequent_indent = indent.following_lines

    @contextmanager
    def indent_increase(self, delta: Indent):
        self.push_indent_increase(delta)
        yield
        self.pop_indent()
