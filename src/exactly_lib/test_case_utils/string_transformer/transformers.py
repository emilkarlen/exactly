from typing import Iterable

from exactly_lib.type_system.logic.line_matcher import LineMatcher, original_and_model_iter_from_file_line_iter
from exactly_lib.type_system.logic.string_transformer import StringTransformer, IdentityStringTransformer, \
    SequenceStringTransformer, CustomStringTransformer


class ReplaceStringTransformer(StringTransformer):
    def __init__(self, compiled_regular_expression, replacement: str):
        self._compiled_regular_expression = compiled_regular_expression
        self._replacement = replacement

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regular_expression.pattern

    @property
    def replacement(self) -> str:
        return self._replacement

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return (
            self._compiled_regular_expression.sub(self._replacement, line)
            for line in lines
        )

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._compiled_regular_expression))


class SelectStringTransformer(StringTransformer):
    """
    Keeps lines matched by a given :class:`LineMatcher`,
    and discards lines not matched.
    """

    def __init__(self, line_matcher: LineMatcher):
        self._line_matcher = line_matcher

    @property
    def line_matcher(self) -> LineMatcher:
        return self._line_matcher

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return (
            line
            for line, line_matcher_model in original_and_model_iter_from_file_line_iter(lines)
            if self._line_matcher.matches(line_matcher_model)
        )

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._line_matcher))


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
