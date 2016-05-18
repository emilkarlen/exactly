from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.textformat.structure import structures as docs


class DescribedArgument:
    def __init__(self,
                 argument: arg.Argument,
                 description: list,
                 see_also: list = ()):
        """
        :type description: [`ParagraphItem`]
        :type see_also: [`CrossReferenceTarget`]
        """
        self.argument = argument
        self.description = description
        self.see_also = list(see_also)


class Synopsis(tuple):
    """
    Describes an invokation variant.
    """

    def __new__(cls,
                command_line: arg.CommandLine,
                single_line_description: docs.Text = None):
        return tuple.__new__(cls, (command_line, single_line_description))

    @property
    def command_line(self) -> arg.CommandLine:
        return self[0]

    @property
    def maybe_single_line_description(self) -> docs.Text:
        """
        :return: `None` if this isn't needed.
        """
        return self[1]
