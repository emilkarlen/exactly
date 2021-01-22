from exactly_lib.symbol.value_type import ValueType, LogicValueType

LOGIC_VALUE_TYPE_2_VALUE_TYPE = {
    LogicValueType.INTEGER_MATCHER: ValueType.INTEGER_MATCHER,
    LogicValueType.LINE_MATCHER: ValueType.LINE_MATCHER,
    LogicValueType.FILE_MATCHER: ValueType.FILE_MATCHER,
    LogicValueType.FILES_MATCHER: ValueType.FILES_MATCHER,
    LogicValueType.STRING_MATCHER: ValueType.STRING_MATCHER,
    LogicValueType.STRING_TRANSFORMER: ValueType.STRING_TRANSFORMER,
    LogicValueType.PROGRAM: ValueType.PROGRAM,
    LogicValueType.FILES_CONDITION: ValueType.FILES_CONDITION,
}