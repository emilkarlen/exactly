from exactly_lib.common.help.see_also import SeeAlsoUrlInfo
from exactly_lib.common.help.syntax_contents_structure import cli_argument_syntax_element_description, \
    invokation_variant_from_args
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.impls.types.regex import parse_regex
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

_IGNORE_CASE_ARGUMENT = a.Option(parse_regex.IGNORE_CASE_OPTION_NAME)

_CL_ARGUMENTS = [
    a.Single(a.Multiplicity.OPTIONAL,
             _IGNORE_CASE_ARGUMENT),
    a.Choice.of_multiple_single_argument_choices(
        a.Multiplicity.MANDATORY,
        (syntax_elements.STRING_SYNTAX_ELEMENT.argument,
         syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.argument,)
    ),
]

SEE_ALSO_URL_INFO = SeeAlsoUrlInfo('Python regular expressions',
                                   'https://docs.python.org/3/library/re.html#regular-expression-syntax')

_DESCRIPTION_OF_IGNORE_CASE_OPTION = """\
Makes the matching ignore case.
"""

DOCUMENTATION = syntax_element_documentation(
    None,
    syntax_elements.REGEX_SYNTAX_ELEMENT,
    [],
    (),
    [
        invokation_variant_from_args(_CL_ARGUMENTS),
    ],
    [
        cli_argument_syntax_element_description(_IGNORE_CASE_ARGUMENT,
                                                TextParser().fnap(_DESCRIPTION_OF_IGNORE_CASE_OPTION))
    ],
    [
        syntax_elements.STRING_SYNTAX_ELEMENT.cross_reference_target,
        syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.cross_reference_target,
        SEE_ALSO_URL_INFO,
    ]
)
