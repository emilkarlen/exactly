from exactly_lib.help.actors.contents_structure import ActorDocumentation
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.document import SectionContents


class SingleCommandLineActorDocumentationBase(ActorDocumentation):
    def act_phase_contents_syntax(self) -> SectionContents:
        from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
        format_map = {
            'LINE_COMMENT_MARKER': LINE_COMMENT_MARKER,
        }
        return SectionContents(normalize_and_parse(_ACT_PHASE_CONTENTS_SYNTAX.format_map(format_map)))


_ACT_PHASE_CONTENTS_SYNTAX = """\
Empty, and comment lines, are ignored.


Comment lines are lines beginning with {LINE_COMMENT_MARKER}
(optionally preceded by space).
"""
