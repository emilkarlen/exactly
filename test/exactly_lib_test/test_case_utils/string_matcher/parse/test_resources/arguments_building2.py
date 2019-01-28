from exactly_lib.definitions import expression
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import Quantifier


class StringMatcherArg:
    """Generate source using __str__"""
    pass


class Empty(StringMatcherArg):
    def __str__(self):
        return matcher_options.EMPTY_ARGUMENT


class Transformed(StringMatcherArg):
    def __init__(self,
                 transformer: str,
                 on_transformed: StringMatcherArg):
        self.transformer = transformer
        self.on_transformed = on_transformed

    def __str__(self):
        return ' '.join([
            option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            self.transformer,
            str(self.on_transformed),
        ])


class NumLines(StringMatcherArg):
    def __init__(self, condition: str):
        self._condition = condition

    def __str__(self):
        return matcher_options.NUM_LINES_ARGUMENT + ' ' + self._condition


class Equals(StringMatcherArg):
    def __init__(self, string_argument: str):
        """
        :param string_argument: Must be a single token.
        """
        self._string_argument = string_argument

    def __str__(self):
        return matcher_options.EQUALS_ARGUMENT + ' ' + self._string_argument


class LineMatches(StringMatcherArg):
    def __init__(self,
                 quantifier: Quantifier,
                 line_matcher: str):
        self.quantifier = quantifier
        self._condition = line_matcher

    def __str__(self):
        return '{any_or_every} {line} {quantifier_separator} {condition}'.format(
            any_or_every=instruction_arguments.QUANTIFIER_ARGUMENTS[self.quantifier],
            line=matcher_options.LINE_ARGUMENT,
            quantifier_separator=instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
            condition=self._condition,
        )


class Not(StringMatcherArg):
    def __init__(self, matcher: StringMatcherArg):
        self.matcher = matcher

    def __str__(self):
        return expression.NOT_OPERATOR_NAME + ' ' + str(self.matcher)
