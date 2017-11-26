from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.util.cli_syntax.elements import argument as a


def file_contents_assertion_arguments() -> list:
    file_contents_arg = a.Single(a.Multiplicity.MANDATORY,
                                 syntax_elements.FILE_CONTENTS_MATCHER.argument)

    optional_not_arg = negation_of_predicate.optional_negation_argument_usage()

    optional_transformation_option = a.Single(a.Multiplicity.OPTIONAL,
                                              instruction_arguments.LINES_TRANSFORMATION_ARGUMENT)
    return [optional_transformation_option,
            optional_not_arg,
            file_contents_arg]
