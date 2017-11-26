from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.instructions.assert_.utils.file_contents.syntax.file_contents_matcher import \
    FileContentsMatcherHelp

_HELPER = FileContentsMatcherHelp()

DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_elements.FILE_CONTENTS_MATCHER,
                                             [],
                                             _HELPER.invokation_variants(),
                                             _HELPER.referenced_syntax_element_descriptions(),
                                             _HELPER.see_also_targets())
