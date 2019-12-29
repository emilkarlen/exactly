from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.syntax import OPERATOR_ARGUMENT
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser

_MANDATORY_OPERATOR_ARGUMENT = a.Single(a.Multiplicity.MANDATORY,
                                        OPERATOR_ARGUMENT)

_TEXT_PARSER = TextParser({
    'INTEGER': syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
})

_DESCRIPTION_OF_COMPARISON_WITH_OPERATOR = """\
Matches if, and only if, the actual value satisfies the comparison.


The actual value that is matched serves as the left hand side in the comparison.
"""


def _operator_syntax_element_description() -> SyntaxElementDescription:
    operators_list = ' '.join(sorted(comparators.NAME_2_OPERATOR.keys()))
    operator_text = 'One of ' + operators_list
    return SyntaxElementDescription(OPERATOR_ARGUMENT.name,
                                    docs.paras(operator_text))


DOCUMENTATION = syntax_element_documentation(
    None,
    syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT,
    [],
    invokation_variants=[
        InvokationVariant(cl_syntax.cl_syntax_for_args([
            _MANDATORY_OPERATOR_ARGUMENT,
            syntax_elements.INTEGER_SYNTAX_ELEMENT.single_mandatory,
        ]),
            _TEXT_PARSER.fnap(_DESCRIPTION_OF_COMPARISON_WITH_OPERATOR))
    ]
    ,
    syntax_element_descriptions=[
        _operator_syntax_element_description(),
    ],
    see_also_targets=[
        syntax_elements.INTEGER_SYNTAX_ELEMENT.cross_reference_target,
    ]
)
