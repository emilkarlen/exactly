from shellcheck_lib.document.syntax import section_header


class SectionName:
    """
    Name of a section in a section-document, with formats for str.format().

    Supports a number of formats, used as format-specifiers:

    $ 'The section {my_section:emphasis} ...'.format(my_section)
    """

    SYNTAX = 'syntax'
    PLAIN = 'plain'
    EMPHASIS = 'emphasis'
    DEFAULT = ''

    def __init__(self, name: str):
        self._name = name
        self._formats = {
            self.SYNTAX: section_header(name),
            self.PLAIN: name,
            self.EMPHASIS: emphasis(name),
            self.DEFAULT: emphasis(name),
        }

    @property
    def plain(self) -> str:
        return self._formats[self.PLAIN]

    @property
    def emphasis(self) -> str:
        return self._formats[self.EMPHASIS]

    @property
    def syntax(self) -> str:
        return self._formats[self.SYNTAX]

    def __str__(self, *args, **kwargs):
        return self._name

    def __format__(self, format_spec):
        try:
            return self._formats[format_spec]
        except KeyError:
            raise ValueError('Invalid section format: "%s"' % format_spec)


def emphasis(s: str) -> str:
    return '"' + s + '"'
