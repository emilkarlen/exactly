from exactly_lib.test_case_utils.condition.comparators import ComparisonOperator
from exactly_lib_test.test_resources import argument_renderer as args
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer

IntegerMatcherArg = ArgumentElementsRenderer


def comparison(comparator: ComparisonOperator,
               lhs: IntegerMatcherArg,
               ) -> IntegerMatcherArg:
    return args.SequenceOfArguments([
        args.Singleton(comparator.name),
        lhs,
    ])