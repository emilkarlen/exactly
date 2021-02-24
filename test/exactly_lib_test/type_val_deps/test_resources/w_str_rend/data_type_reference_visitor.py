from exactly_lib.type_val_deps.sym_ref.restrictions import WithStrRenderingTypeRestrictions
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect, \
    OrReferenceRestrictions


class TypeWithStrRenderingReferenceRestrictionsVisitor:
    def visit(self, x: WithStrRenderingTypeRestrictions):
        if isinstance(x, ReferenceRestrictionsOnDirectAndIndirect):
            return self.visit_direct_and_indirect(x)
        if isinstance(x, OrReferenceRestrictions):
            return self.visit_or(x)
        raise TypeError('%s is not an instance of %s' % (str(x), str(WithStrRenderingTypeRestrictions)))

    def visit_direct_and_indirect(self, x: ReferenceRestrictionsOnDirectAndIndirect):
        raise NotImplementedError()

    def visit_or(self, x: OrReferenceRestrictions):
        raise NotImplementedError()
