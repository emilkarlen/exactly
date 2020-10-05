from exactly_lib.test_case_utils.condition import comparators


def int_condition(operator: comparators.ComparisonOperator,
                  value: int) -> str:
    return operator.name + ' ' + str(value)


def int_condition__expr(operator: comparators.ComparisonOperator,
                        expression: str) -> str:
    return operator.name + ' ' + expression
