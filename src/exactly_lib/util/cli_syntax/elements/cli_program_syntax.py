from typing import Optional, Sequence, List

from exactly_lib.common.help.see_also import SeeAlsoItem
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.textformat.structure import structures as docs


class DescribedArgument:
    def __init__(self,
                 argument: arg.Argument,
                 description: List[docs.ParagraphItem],
                 see_also_items: Sequence[SeeAlsoItem] = ()):
        self.argument = argument
        self.description = description
        self.see_also_items = list(see_also_items)


class Synopsis(tuple):
    """
    Describes an invokation variant.
    """

    def __new__(cls,
                command_line: arg.CommandLine,
                single_line_description: Optional[docs.Text] = None,
                paragraphs: Sequence[docs.ParagraphItem] = (),
                additional_command_lines: Sequence[arg.CommandLine] = ()):
        return tuple.__new__(cls, (command_line,
                                   single_line_description,
                                   list(paragraphs),
                                   list(additional_command_lines)))

    @property
    def command_line(self) -> arg.CommandLine:
        return self[0]

    @property
    def maybe_single_line_description(self) -> Optional[docs.Text]:
        return self[1]

    @property
    def paragraphs(self) -> List[docs.ParagraphItem]:
        return self[2]

    @property
    def additional_command_lines(self) -> Sequence[arg.CommandLine]:
        return self[3]

    @property
    def command_lines(self) -> List[arg.CommandLine]:
        return [self.command_line] + list(self.additional_command_lines)
