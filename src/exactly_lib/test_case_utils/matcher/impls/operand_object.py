from typing import Generic, TypeVar, Sequence, Set, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.condition.comparison_structures import OperandResolver, OperandValue
from exactly_lib.test_case_utils.matcher.object import ObjectResolver, ObjectValue
from exactly_lib.test_case_utils.svh_exception import SvhException
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class ObjectValueOfOperandValue(Generic[T], ObjectValue[T]):
    def __init__(self, operand: OperandValue[T]):
        self._operand = operand

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._operand.resolving_dependencies()

    def value_of_any_dependency(self, tcds: HomeAndSds) -> T:
        return self._operand.value_of_any_dependency(tcds)


class ObjectResolverOfOperandResolver(Generic[T], ObjectResolver[T]):
    def __init__(self, operand: OperandResolver):
        super().__init__(operand.property_name)
        self._operand = operand
        self._validator = _Validator(operand)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._operand.references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> ObjectValue[T]:
        return ObjectValueOfOperandValue(self._operand.resolve(symbols))


class _Validator(PreOrPostSdsValidator):
    def __init__(self, operand: OperandResolver):
        self._operand = operand

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        try:
            self._operand.validate_pre_sds(environment)
        except SvhException as ex:
            return ex.err_msg

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        pass
