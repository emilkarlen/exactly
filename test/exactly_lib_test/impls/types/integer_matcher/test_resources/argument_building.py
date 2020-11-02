from exactly_lib.impls.types.condition.comparators import ComparisonOperator
from exactly_lib_test.test_resources import argument_renderer as args
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer

IntegerMatcherArg = ArgumentElementsRenderer


def comparison(comparator: ComparisonOperator,
               rhs: IntegerMatcherArg,
               ) -> IntegerMatcherArg:
    return args.SequenceOfArguments([
        args.Singleton(comparator.name),
        rhs,
    ])


def comparison2(comparator: ComparisonOperator,
                rhs: int,
                ) -> IntegerMatcherArg:
    return args.SequenceOfArguments([
        args.Singleton(comparator.name),
        args.Singleton(str(rhs)),
    ])
