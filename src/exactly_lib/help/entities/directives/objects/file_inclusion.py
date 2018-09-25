from typing import Sequence

from exactly_lib.common.help.abs_or_rel_path import abs_or_rel_path_of_existing
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args, \
    SyntaxElementDescription, cli_argument_syntax_element_description
from exactly_lib.definitions.entity import directives
from exactly_lib.help.entities.directives.contents_structure import DirectiveDocumentation
from exactly_lib.processing.parse import file_inclusion_directive_parser
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class FileInclusionDocumentation(DirectiveDocumentation):
    def __init__(self):
        super().__init__(directives.INCLUDING_DIRECTIVE_INFO)
        self.file_argument = a.Named(file_inclusion_directive_parser.FILE_ARGUMENT_NAME)
        self._tp = TextParser({
            'including_directive': self.info.singular_name,
            'FILE': self.file_argument.name,
        })

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        return [
            invokation_variant_from_args([a.Single(a.Multiplicity.MANDATORY,
                                                   self.file_argument)])
        ]

    def syntax_element_descriptions(self) -> Sequence[SyntaxElementDescription]:
        return [
            cli_argument_syntax_element_description(self.file_argument,
                                                    abs_or_rel_path_of_existing(
                                                        'file',
                                                        self.file_argument.name,
                                                        _FILE_RELATIVITY_ROOT
                                                    ))
        ]

    def description(self) -> SectionContents:
        return docs.section_contents(self._tp.fnap(_MAIN_DESCRIPTION_REST))


_FILE_RELATIVITY_ROOT = 'directory of the current source file'

_MAIN_DESCRIPTION_REST = """\
The effect of including a file is equivalent to having the
contents of the included file in the including file;
except that the current phase of the including file
cannot be changed by an included file.


The default phase of the included file is the phase
from which the file is included.


The included file may contain contents of
different phases,
by declaring different phases just as in a main test case file.

But the phase of the including file is
not changed.
"""
