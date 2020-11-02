from abc import ABC
from typing import Sequence, List

from exactly_lib.definitions import logic
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.symbol import symbol_syntax
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import Quantifier
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.tcfs.test_resources.path_arguments import PathArgument
from exactly_lib_test.test_resources.argument_renderer import elements_for_binary_operator_arg
from exactly_lib_test.test_resources.argument_renderers import FileOrString, FileOrStringAsString, FileOrStringAsFile, \
    FileOrStringAsHereDoc, HereDocument
from exactly_lib_test.test_resources.matcher_argument import MatcherArgument
from exactly_lib_test.test_resources.strings import WithToString


class StringMatcherArg(MatcherArgument, ABC):
    """Generate source using __str__"""
    pass


class Empty(StringMatcherArg):
    @property
    def elements(self) -> List[WithToString]:
        return [matcher_options.EMPTY_ARGUMENT]


class SymbolReference(StringMatcherArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    @property
    def elements(self) -> List[WithToString]:
        return [self.symbol_name]


class SymbolReferenceWReferenceSyntax(StringMatcherArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    @property
    def elements(self) -> List[WithToString]:
        return [symbol_syntax.symbol_reference_syntax_for_name(self.symbol_name)]


class Transformed(StringMatcherArg):
    def __init__(self,
                 transformer: str,
                 on_transformed: StringMatcherArg):
        self.transformer = transformer
        self.on_transformed = on_transformed

    @property
    def elements(self) -> List[WithToString]:
        return [
            option_syntax(string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            self.transformer,
            str(self.on_transformed),
        ]


class NumLines(StringMatcherArg):
    def __init__(self, condition: str):
        self._condition = condition

    @property
    def elements(self) -> List[WithToString]:
        return [matcher_options.NUM_LINES_ARGUMENT, self._condition]


class Equals(StringMatcherArg):
    def __init__(self, contents: FileOrString):
        self.contents = contents

    @staticmethod
    def eq_string(string: str) -> 'Equals':
        return Equals(FileOrStringAsString(string))

    @staticmethod
    def eq_file(file: PathArgument) -> 'Equals':
        return Equals(FileOrStringAsFile(file))

    @staticmethod
    def eq_here_doc(separator: str, contents_ended_w_new_line: str) -> 'Equals':
        return Equals(FileOrStringAsHereDoc(
            HereDocument(separator, contents_ended_w_new_line)
        ))

    @property
    def elements(self) -> List[WithToString]:
        return [matcher_options.EQUALS_ARGUMENT] + self.contents.elements


class Matches(StringMatcherArg):
    def __init__(self, regex: str):
        """
        :param string_argument: Must be a single token.
        """
        self._regex = regex

    @property
    def elements(self) -> List[WithToString]:
        return [matcher_options.MATCHES_ARGUMENT, self._regex]


class Quantification(StringMatcherArg):
    def __init__(self,
                 quantifier: Quantifier,
                 line_matcher: str):
        self.quantifier = quantifier
        self._condition = line_matcher

    @property
    def elements(self) -> List[WithToString]:
        return [
            logic.QUANTIFIER_ARGUMENTS[self.quantifier],
            matcher_options.LINE_ARGUMENT,
            logic.QUANTIFICATION_SEPARATOR_ARGUMENT,
            self._condition,
        ]


class RunProgram(StringMatcherArg):
    def __init__(self, program: ArgumentElements):
        self.program = program

    @property
    def as_argument_elements(self) -> ArgumentElements:
        run_primitive = ArgumentElements([matcher_options.RUN_PROGRAM_ARGUMENT])
        return run_primitive.append_to_first_and_following_lines(self.program)

    def __str__(self):
        return self.as_argument_elements.as_arguments.as_single_string

    @property
    def elements(self) -> List[WithToString]:
        return self.as_argument_elements.as_elements


class Not(StringMatcherArg):
    def __init__(self, matcher: StringMatcherArg):
        self.matcher = matcher

    @property
    def elements(self) -> List[WithToString]:
        return [logic.NOT_OPERATOR_NAME] + self.matcher.elements


class Parenthesis(StringMatcherArg):
    def __init__(self, string_matcher: StringMatcherArg):
        self.string_matcher = string_matcher

    @property
    def elements(self) -> List[WithToString]:
        return ['('] + self.string_matcher.elements + [')']


class BinaryOperator(StringMatcherArg):
    def __init__(self,
                 operator: str,
                 operands: Sequence[StringMatcherArg]):
        self.operator = operator
        self.operands = operands

    @property
    def elements(self) -> List[WithToString]:
        return elements_for_binary_operator_arg(self.operator, self.operands)


def conjunction(operands: Sequence[StringMatcherArg]) -> BinaryOperator:
    return BinaryOperator(logic.AND_OPERATOR_NAME, operands)


def disjunction(operands: Sequence[StringMatcherArg]) -> BinaryOperator:
    return BinaryOperator(logic.OR_OPERATOR_NAME, operands)


class Custom(StringMatcherArg):
    def __init__(self, string_matcher: WithToString):
        self.string_matcher = string_matcher

    @property
    def elements(self) -> List[WithToString]:
        return [self.string_matcher]
