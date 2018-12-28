from exactly_lib.util.logic_types import ExpectationType, Quantifier
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import pfh_expectation_type_config


class InstructionArgumentsConstructorForExpTypeAndQuantifier:
    """"Constructs instruction arguments for a variant of (expectation type, any-or-every, transformer)."""

    def construct(self,
                  expectation_type: ExpectationType,
                  quantifier: Quantifier,
                  ) -> str:
        raise NotImplementedError('abstract method')


class ArgumentsConstructorForPossiblyInvalidSyntax(InstructionArgumentsConstructorForExpTypeAndQuantifier):
    def __init__(self,
                 line_matcher: str,
                 superfluous_args_str: str = '',
                 transformer: str = ''):
        self.transformer = transformer
        self.line_matcher = line_matcher
        self.superfluous_args_str = superfluous_args_str
        self._common_arguments = arguments_building.CommonArgumentsConstructor(transformer)

    def construct(self,
                  expectation_type: ExpectationType,
                  quantifier: Quantifier,
                  ) -> str:
        arguments_constructor = arguments_building.ImplicitActualFileArgumentsConstructor(
            self._common_arguments,
            arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier, self.line_matcher),
        )
        etc = pfh_expectation_type_config(expectation_type)

        superfluous_args_str = self.superfluous_args_str
        if superfluous_args_str:
            superfluous_args_str = ' ' + superfluous_args_str
        return arguments_constructor.apply(etc) + superfluous_args_str


class InstructionArgumentsConstructorForValidSyntax(InstructionArgumentsConstructorForExpTypeAndQuantifier):
    def __init__(self,
                 common_arguments: arguments_building.CommonArgumentsConstructor,
                 line_matcher: str):
        self.common_arguments = common_arguments
        self.line_matcher = line_matcher
        self._common_arguments = common_arguments

    def construct(self,
                  expectation_type: ExpectationType,
                  quantifier: Quantifier,
                  ) -> str:
        arguments_constructor = arguments_building.ImplicitActualFileArgumentsConstructor(
            self._common_arguments,
            arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier, self.line_matcher),
        )
        etc = pfh_expectation_type_config(expectation_type)
        return arguments_constructor.apply(etc)


def args_constructor_for(line_matcher: str,
                         transformer: str = '') -> InstructionArgumentsConstructorForExpTypeAndQuantifier:
    return InstructionArgumentsConstructorForValidSyntax(
        arguments_building.CommonArgumentsConstructor(transformer),
        line_matcher)
