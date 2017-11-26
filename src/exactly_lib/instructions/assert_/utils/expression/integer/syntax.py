from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help_texts.instruction_arguments import INTEGER_ARGUMENT
from exactly_lib.instructions.assert_.utils.expression import comparators
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs

OPERATOR_ARGUMENT = a.Named('OPERATOR')


def syntax_element_descriptions(integer_text: str = 'An integer.') -> list:
    operators_list = ' '.join(sorted(comparators.NAME_2_OPERATOR.keys()))
    operator_text = 'One of ' + operators_list
    return [
        SyntaxElementDescription(OPERATOR_ARGUMENT.name,
                                 docs.paras(operator_text)),
        SyntaxElementDescription(INTEGER_ARGUMENT.name,
                                 docs.paras(integer_text)),
    ]


def syntax_element_descriptions_with_negation_operator(
        integer_text: str = 'An integer') -> list:
    return [negation_of_predicate.syntax_element_description()] + syntax_element_descriptions(integer_text)
