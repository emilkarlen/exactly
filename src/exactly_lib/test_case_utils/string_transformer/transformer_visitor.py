from exactly_lib.test_case_utils.string_transformer.impl.replace import ReplaceStringTransformer
from exactly_lib.test_case_utils.string_transformer.impl.select import SelectStringTransformer
from exactly_lib.type_system.logic.string_transformer import StringTransformer, CustomStringTransformer, \
    SequenceStringTransformer, IdentityStringTransformer


class StringTransformerStructureVisitor:
    """
    Visits all variants of :class:`StringTransformer`.

    The existence of this class means that the structure of :class:`StringTransformer`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.
    """

    def visit(self, transformer: StringTransformer):
        if isinstance(transformer, ReplaceStringTransformer):
            return self.visit_replace(transformer)
        if isinstance(transformer, SelectStringTransformer):
            return self.visit_select(transformer)
        if isinstance(transformer, CustomStringTransformer):
            return self.visit_custom(transformer)
        if isinstance(transformer, SequenceStringTransformer):
            return self.visit_sequence(transformer)
        elif isinstance(transformer, IdentityStringTransformer):
            return self.visit_identity(transformer)
        else:
            raise TypeError('Unknown {}: {}'.format(StringTransformer,
                                                    str(transformer)))

    def visit_identity(self, transformer: IdentityStringTransformer):
        raise NotImplementedError('abstract method')

    def visit_sequence(self, transformer: SequenceStringTransformer):
        raise NotImplementedError('abstract method')

    def visit_replace(self, transformer: ReplaceStringTransformer):
        raise NotImplementedError('abstract method')

    def visit_select(self, transformer: SelectStringTransformer):
        raise NotImplementedError('abstract method')

    def visit_custom(self, transformer: CustomStringTransformer):
        raise NotImplementedError('abstract method')
