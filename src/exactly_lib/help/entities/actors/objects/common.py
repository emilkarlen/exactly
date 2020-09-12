from exactly_lib.util.textformat.textformat_parser import TextParser


class ActPhaseDocumentationSyntaxBase:
    def __init__(self, text_parser: TextParser):
        self._parser = text_parser


SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH = """\
Comment lines are lines beginning with {LINE_COMMENT_MARKER}
(optionally preceded by space).
"""
