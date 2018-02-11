from exactly_lib.common.help.see_also import SeeAlsoUrlInfo
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, cli_argument_syntax_element_description
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.test_case_utils.parse import parse_reg_ex
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

_IGNORE_CASE_ARGUMENT = a.Option(parse_reg_ex.IGNORE_CASE_OPTION_NAME)

_CL_ARGUMENTS = [
    a.Single(a.Multiplicity.OPTIONAL,
             _IGNORE_CASE_ARGUMENT),
    a.Single(a.Multiplicity.MANDATORY,
             syntax_elements.STRING_SYNTAX_ELEMENT.argument),

]

_TEXT_PARSER = TextParser({
    'STRING': syntax_elements.STRING_SYNTAX_ELEMENT.argument.name,
    'SYMBOL_REFERENCE': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.argument.name,
})

SEE_ALSO_URL_INFO = SeeAlsoUrlInfo('Python regular expressions',
                                   'https://docs.python.org/3/library/re.html#regular-expression-syntax')

_DESCRIPTION_OF_IGNORE_CASE_OPTION = """\
Makes the matching ignore case.
"""

_MAIN_DESCRIPTION_REST = """\
Any {SYMBOL_REFERENCE} in {STRING} is NOT substituted!
"""

DOCUMENTATION = syntax_element_documentation(
    None,
    syntax_elements.REGEX_SYNTAX_ELEMENT,
    _TEXT_PARSER.fnap(_MAIN_DESCRIPTION_REST),
    [
        InvokationVariant(
            cl_syntax.cl_syntax_for_args(_CL_ARGUMENTS)
        ),
    ],
    [
        cli_argument_syntax_element_description(_IGNORE_CASE_ARGUMENT,
                                                _TEXT_PARSER.fnap(_DESCRIPTION_OF_IGNORE_CASE_OPTION))
    ],
    [
        syntax_elements.STRING_SYNTAX_ELEMENT.cross_reference_target,
        SEE_ALSO_URL_INFO,
    ]
)
