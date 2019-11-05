from typing import Generic, TypeVar, Sequence, Set, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.condition.comparison_structures import OperandResolver, OperandValue
from exactly_lib.test_case_utils.matcher.object import ObjectResolver, ObjectValue
from exactly_lib.test_case_utils.svh_exception import SvhException
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class ObjectValueOfOperandValue(Generic[T], ObjectValue[T]):
    def __init__(self,
                 validator: PreOrPostSdsValueValidator,
                 operand: OperandValue[T],
                 ):
        self._validator = validator
        self._operand = operand

    def describer(self) -> DetailsRenderer:
        return self._operand.describer()

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._operand.resolving_dependencies()

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: HomeAndSds) -> T:
        return self._operand.value_of_any_dependency(tcds)


class ObjectResolverOfOperandResolver(Generic[T], ObjectResolver[T]):
    def __init__(self, operand: OperandResolver):
        self._operand = operand

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._operand.references

    def resolve(self, symbols: SymbolTable) -> ObjectValue[T]:
        return ObjectValueOfOperandValue(
            _Validator(symbols, self._operand),
            self._operand.resolve(symbols),
        )


class _Validator(PreOrPostSdsValueValidator):
    def __init__(self,
                 symbols: SymbolTable,
                 operand: OperandResolver,
                 ):
        self._symbols = symbols
        self._operand = operand

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        try:
            self._operand.validate_pre_sds(PathResolvingEnvironmentPreSds(hds, self._symbols))
        except SvhException as ex:
            return ex.err_msg

    def validate_post_sds_if_applicable(self, tcds: HomeAndSds) -> Optional[TextRenderer]:
        pass
