from exactly_lib.type_system.value_type import ValueType, LogicValueType

LOGIC_VALUE_TYPE_2_VALUE_TYPE = {
    LogicValueType.LINE_MATCHER: ValueType.LINE_MATCHER,
    LogicValueType.FILE_MATCHER: ValueType.FILE_MATCHER,
    LogicValueType.FILES_MATCHER: ValueType.FILES_MATCHER,
    LogicValueType.STRING_MATCHER: ValueType.STRING_MATCHER,
    LogicValueType.STRING_TRANSFORMER: ValueType.STRING_TRANSFORMER,
    LogicValueType.PROGRAM: ValueType.PROGRAM,
}
