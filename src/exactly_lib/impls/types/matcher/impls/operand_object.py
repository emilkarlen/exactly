from typing import Generic, TypeVar, Sequence, Set, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.exception.svh_exception import SvhException
from exactly_lib.impls.types.condition.comparison_structures import OperandSdv, OperandDdv
from exactly_lib.impls.types.matcher.object import ObjectSdv, ObjectDdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreSds
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class ObjectValueOfOperandDdv(Generic[T], ObjectDdv[T]):
    def __init__(self,
                 validator: DdvValidator,
                 operand: OperandDdv[T],
                 ):
        self._validator = validator
        self._operand = operand

    def describer(self) -> DetailsRenderer:
        return self._operand.describer()

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._operand.resolving_dependencies()

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> T:
        return self._operand.value_of_any_dependency(tcds)


class ObjectSdvOfOperandSdv(Generic[T], ObjectSdv[T]):
    def __init__(self, operand: OperandSdv):
        self._operand = operand

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._operand.references

    def resolve(self, symbols: SymbolTable) -> ObjectDdv[T]:
        return ObjectValueOfOperandDdv(
            _Validator(symbols, self._operand),
            self._operand.resolve(symbols),
        )


class _Validator(DdvValidator):
    def __init__(self,
                 symbols: SymbolTable,
                 operand: OperandSdv,
                 ):
        self._symbols = symbols
        self._operand = operand

    def validate_pre_sds_if_applicable(self, hds: HomeDs) -> Optional[TextRenderer]:
        try:
            self._operand.validate_pre_sds(PathResolvingEnvironmentPreSds(hds, self._symbols))
        except SvhException as ex:
            return ex.err_msg

    def validate_post_sds_if_applicable(self, tcds: TestCaseDs) -> Optional[TextRenderer]:
        pass
