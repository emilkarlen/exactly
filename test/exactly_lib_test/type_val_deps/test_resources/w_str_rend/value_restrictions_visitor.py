from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import \
    ArbitraryValueWStrRenderingRestriction, PathAndRelativityRestriction

T = TypeVar('T')


class ProdValueRestrictionVariantsVisitor(Generic[T], ABC):
    """Handles all variants of value restrictions that are supported in production"""

    def visit(self, x: ValueRestriction) -> T:
        if isinstance(x, ArbitraryValueWStrRenderingRestriction):
            return self.visit_any(x)
        if isinstance(x, PathAndRelativityRestriction):
            return self.visit_path_relativity(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(ValueRestriction)))

    @abstractmethod
    def visit_any(self, x: ArbitraryValueWStrRenderingRestriction) -> T:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def visit_path_relativity(self, x: PathAndRelativityRestriction) -> T:
        raise NotImplementedError('abstract method')
