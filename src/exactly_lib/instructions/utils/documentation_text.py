from exactly_lib.common.instruction_documentation import SyntaxElementDescription
from exactly_lib.help.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils.relative_path_options_documentation import RelOptionRenderer
from exactly_lib.util.cli_syntax.elements.argument import Named
from exactly_lib.util.textformat.structure import structures as docs


def paths_uses_posix_syntax() -> list:
    return docs.paras("""Paths uses posix syntax.""")


def default_relativity(path_arg_name: str,
                       default_relativity_location: str) -> list:
    return docs.paras(_DEFAULT_RELATIVITY
                      .format(path=path_arg_name,
                              default_relativity_location=default_relativity_location))


def relativity_syntax_element_description(path_that_may_be_relative: Named,
                                          iter_of_rel_option_type: iter) -> SyntaxElementDescription:
    renderer = RelOptionRenderer(path_that_may_be_relative.name)
    return SyntaxElementDescription(RELATIVITY_ARGUMENT.name,
                                    [renderer.list_for(iter_of_rel_option_type)])


RELATIVITY_ARGUMENT = Named('RELATIVITY')

PATH_ARGUMENT = Named('PATH')

FILE_ARGUMENT = Named('FILE')

DIR_ARGUMENT = Named('DIR')

_DEFAULT_RELATIVITY = """\
By default {path} is relative the {default_relativity_location}.
"""

HERE_DOC_SUFFIX = '<<MARKER <lines> MARKER'


def a_path_that_is_relative_the(syntax_element_name,
                                relativity_root) -> SyntaxElementDescription:
    syntax_element_name_str = syntax_element_name
    if isinstance(syntax_element_name, Named):
        syntax_element_name_str = syntax_element_name.name
    relativity_root_str = relativity_root
    if isinstance(relativity_root_str, ConceptDocumentation):
        relativity_root_str = formatting.concept(relativity_root.name().singular)
    text = 'A path that is relative to the ' + relativity_root_str + '.'
    return SyntaxElementDescription(syntax_element_name_str,
                                    docs.paras(text))
