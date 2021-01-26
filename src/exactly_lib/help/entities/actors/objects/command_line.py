from typing import List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import conf_params, syntax_elements, types
from exactly_lib.definitions.entity.actors import COMMAND_LINE_ACTOR
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.help.entities.actors.objects.common import \
    SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.render import doc_utils
from exactly_lib.impls.actors import common as rel_opt_conf
from exactly_lib.impls.types.path import relative_path_options_documentation
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class CommandLineActorDocumentation(ActorDocumentation):
    def __init__(self):
        super().__init__(COMMAND_LINE_ACTOR)
        self._tp = TextParser({
            'LINE_COMMENT_MARKER': formatting.string_constant(LINE_COMMENT_MARKER),
            'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
            'STRING_TRANSFORMER': syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
            'PATH': syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
            'path': types.PATH_TYPE_INFO.name,
            'executable_file': formatting.misc_name_with_formatting(misc_texts.EXECUTABLE_FILE),
            'relativity': formatting.misc_name_with_formatting(misc_texts.RELATIVITY),
            'stdout': misc_texts.STDOUT,
            'stdin': misc_texts.STDIN,
            'os_process': misc_texts.OS_PROCESS_NAME,
            'setup_phase': phase_names.SETUP,
        })

    def act_phase_contents(self) -> doc.SectionContents:
        return doc.SectionContents(self._tp.fnap(_ACT_PHASE_CONTENTS))

    def act_phase_contents_syntax(self) -> doc.SectionContents:
        return doc.SectionContents(
            self._tp.fnap(SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH),
            self._act_phase_contents_syntax_sub_sections(),
        )

    def notes(self) -> SectionContents:
        return docs.section_contents(
            sub_sections=[
                docs.section(
                    self._tp.text('{path:/u} {relativity:s}'),
                    self._notes_section_paragraphs(),
                ),
                docs.section(
                    self._tp.text(misc_texts.STDIN.capitalize()),
                    self._tp.fnap(_STDIN_DESCRIPTION),
                ),
                docs.section(
                    self._tp.text('Transformations'),
                    self._tp.fnap(_TRANSFORMATION_DESCRIPTION),
                ),
            ]
        )

    def _act_phase_contents_syntax_sub_sections(self) -> List[doc.Section]:
        return [
            doc_utils.synopsis_section(
                invokation_variants_content(None,
                                            self._invokation_variants(),
                                            ())
            )
        ]

    @staticmethod
    def _invokation_variants() -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([syntax_elements.PROGRAM_SYNTAX_ELEMENT.single_mandatory]),
        ]

    def _notes_section_paragraphs(self) -> List[ParagraphItem]:
        ret_val = self._tp.fnap(_PATH_RELATIVITY_HEADER)

        ret_val += relative_path_options_documentation.path_element_relativity_paragraphs(
            rel_opt_conf.REL_OPTIONS_CONFIGURATION
        )

        return ret_val

    def _see_also_specific(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            conf_params.HDS_ACT_DIRECTORY_CONF_PARAM_INFO,
            syntax_elements.PATH_SYNTAX_ELEMENT,
            syntax_elements.PROGRAM_SYNTAX_ELEMENT,
        ])


DOCUMENTATION = CommandLineActorDocumentation()

_ACT_PHASE_CONTENTS = """\
A single {PROGRAM} element.


Any number of empty lines and comment lines are allowed.
"""

_PATH_RELATIVITY_HEADER = """\
When {PROGRAM} has the form of the {PATH} of {executable_file:a}:
"""

_STDIN_DESCRIPTION = """\
If {PROGRAM} defines {stdin},
then the {stdin} of the {os_process}
is the {stdin} defined for {PROGRAM}
followed by the {stdin} set in the {setup_phase:emphasis} phase.
"""

_TRANSFORMATION_DESCRIPTION = """\
If {PROGRAM} includes a transformation (via a {STRING_TRANSFORMER}),
then the transformation is applied to {stdout}
of the {os_process}.
"""
