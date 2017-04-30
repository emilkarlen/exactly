from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.utils.names import formatting
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs


class CommandLineRenderingHelper:
    """
    Utility class for rendering command lines.
    """

    CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

    ARG_SYNTAX_RENDERER = cli_program_syntax.ArgumentInArgumentDescriptionRenderer()

    def cl_syntax_for_args(self, argument_usages: list) -> str:
        cl = a.CommandLine(argument_usages)
        return self.cl_syntax(cl)

    def cl_syntax(self, command_line: a.CommandLine) -> str:
        return self.CL_SYNTAX_RENDERER.as_str(command_line)

    def arg_syntax(self, arg: a.Argument) -> str:
        return self.ARG_SYNTAX_RENDERER.visit(arg)

    def cli_argument_syntax_element_description(self,
                                                argument: a.Argument,
                                                description_rest: list) -> SyntaxElementDescription:
        return SyntaxElementDescription(self.arg_syntax(argument),
                                        description_rest)


def paths_uses_posix_syntax() -> list:
    return docs.paras("""Paths uses posix syntax.""")


def here_document_syntax_element_description(instruction_name: str,
                                             here_document_argument: a.Named) -> SyntaxElementDescription:
    s = _HERE_DOCUMENT_DESCRIPTION.format(instruction_name=instruction_name)
    return SyntaxElementDescription(here_document_argument.name,
                                    normalize_and_parse(s))


PATH_ARGUMENT = a.Named('PATH')

FILE_ARGUMENT = a.Named('FILE')

DIR_ARGUMENT = a.Named('DIR')

HERE_DOCUMENT = a.Named('HERE-DOCUMENT')

REG_EX = a.Named('REG-EX')

_HERE_DOCUMENT_DESCRIPTION = """\
A sequence of lines, given using the shell "here document" syntax.


```
{instruction_name} ... <<EOF
<first line>
...
<last line>
EOF
```


Any single-word string may be used instead of "EOF" as marker.
What matters is that the maker at start and end of input
matches.
"""


def a_path_that_is_relative_the(syntax_element_name,
                                relativity_root) -> SyntaxElementDescription:
    syntax_element_name_str = syntax_element_name
    if isinstance(syntax_element_name, a.Named):
        syntax_element_name_str = syntax_element_name.name
    relativity_root_str = relativity_root
    if isinstance(relativity_root_str, ConceptDocumentation):
        relativity_root_str = formatting.concept(relativity_root.name().singular)
    text = 'A path that is relative to the ' + relativity_root_str + '.'
    return SyntaxElementDescription(syntax_element_name_str,
                                    docs.paras(text))
