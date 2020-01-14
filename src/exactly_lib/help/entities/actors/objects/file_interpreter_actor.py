from typing import List

from exactly_lib.actors import file_interpreter as actor
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.definitions import instruction_arguments, formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.actors import FILE_INTERPRETER_ACTOR
from exactly_lib.definitions.test_case.actors import file_interpreter as help_texts
from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.help.entities.actors.objects.common import ARGUMENT_SYNTAX_ELEMENT, \
    SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH, ActPhaseDocumentationSyntaxBase
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.render import doc_utils
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case_utils.documentation.relative_path_options_documentation import path_element_2
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import section_contents
from exactly_lib.util.textformat.textformat_parser import TextParser


class FileInterpreterActorDocumentation(ActorDocumentation):
    CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

    ARG_SYNTAX_RENDERER = cli_program_syntax.ArgumentInArgumentDescriptionRenderer()

    def __init__(self):
        super().__init__(FILE_INTERPRETER_ACTOR)
        self._tp = TextParser({
            'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
            'LINE_COMMENT_MARKER': formatting.string_constant(LINE_COMMENT_MARKER),
        })

    def act_phase_contents(self) -> doc.SectionContents:
        return section_contents(self._tp.fnap(_ACT_PHASE_CONTENTS))

    def act_phase_contents_syntax(self) -> doc.SectionContents:
        documentation = ActPhaseDocumentationSyntax()
        initial_paragraphs = self._tp.fnap(SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH)
        sub_sections = []
        synopsis_section = doc_utils.synopsis_section(
            invokation_variants_content(None,
                                        documentation.invokation_variants(),
                                        documentation.syntax_element_descriptions()))
        sub_sections.append(synopsis_section)
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _see_also_specific(self) -> List[SeeAlsoTarget]:
        return [
            concepts.SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target,
        ]


DOCUMENTATION = FileInterpreterActorDocumentation()


class ActPhaseDocumentationSyntax(ActPhaseDocumentationSyntaxBase):
    def __init__(self):
        self.file = instruction_arguments.FILE_ARGUMENT
        self.argument = a.Named(help_texts.ARGUMENT)
        fm = {
            'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
        }
        super().__init__(TextParser(fm))

    def invokation_variants(self) -> List[InvokationVariant]:
        executable_arg = a.Single(a.Multiplicity.MANDATORY, self.file)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE, self.argument)
        return [
            InvokationVariant(self._cl_syntax_for_args([executable_arg,
                                                        optional_arguments_arg])),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            path_element_2(actor.RELATIVITY_CONFIGURATION,
                           self._parser.fnap(_SOURCE_FILE_SYNTAX_ELEMENT)),
            SyntaxElementDescription(self.argument.name,
                                     self._parser.fnap(ARGUMENT_SYNTAX_ELEMENT)),
        ]


_SOURCE_FILE_SYNTAX_ELEMENT = """\
The path of an existing source code file.
"""

_ACT_PHASE_CONTENTS = """\
A single line which is a file name followed by optional arguments.


The file name and arguments may be quoted according to {shell_syntax_concept}.
"""
