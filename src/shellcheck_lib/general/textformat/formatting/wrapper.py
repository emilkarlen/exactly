from textwrap import TextWrapper


class Indent(tuple):
    def __new__(cls,
                first_line: str,
                following_lines: str):
        return tuple.__new__(cls, (first_line, following_lines))

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

    @property
    def page_width(self) -> int:
        return self.text_wrapper.width

    @property
    def current_indent(self) -> Indent:
        return Indent(self.text_wrapper.initial_indent,
                      self.text_wrapper.subsequent_indent)

    @property
    def saved_indents_stack(self) -> list:
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
        indent = self._saved_indents_stack.pop()
        self.text_wrapper.initial_indent = indent.first_line
        self.text_wrapper.subsequent_indent = indent.following_lines

    def wrap(self, text: str) -> list:
        return self.text_wrapper.wrap(text)
