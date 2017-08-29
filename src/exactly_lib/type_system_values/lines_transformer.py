import functools

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.functional import compose_first_and_second


class LinesTransformer:
    """
    Transforms a sequence of lines, where each line is a string.
    """

    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        raise NotImplementedError('abstract method')

    def __str__(self):
        return type(self).__name__


class IdentityLinesTransformer(LinesTransformer):
    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        raise NotImplementedError('this method should never be called')


class SequenceLinesTransformer(LinesTransformer):
    def __init__(self, transformers: list):
        self._transformers = tuple(transformers)

    @property
    def transformers(self) -> tuple:
        return self._transformers

    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        if not self._transformers:
            return lines
        else:
            return self._sequenced_transformers(tcds)(lines)

    def _sequenced_transformers(self, tcds: HomeAndSds):
        lines_to_lines_transformers = [functools.partial(t.transform, tcds)
                                       for t in self._transformers]

        return functools.reduce(compose_first_and_second, lines_to_lines_transformers)

    def __str__(self):
        return '{}[{}]'.format(type(self).__name__,
                               ','.join(map(str, self._transformers)))


class CustomLinesTransformer(LinesTransformer):
    """
    Base class for built in custom transformers.

    Such a transformer is identified by its name,
    that must be unique.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return '{}({})'.format(type(self).__name__, repr(self._name))


class LinesTransformerStructureVisitor:
    """
    Visits all variants of :class:`FileSelector`.

    The existence of this class means that the structure of :class:`FileSelector`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.
    """

    def visit(self, transformer: LinesTransformer):
        if isinstance(transformer, CustomLinesTransformer):
            return self.visit_custom(transformer)
        if isinstance(transformer, SequenceLinesTransformer):
            return self.visit_sequence(transformer)
        elif isinstance(transformer, IdentityLinesTransformer):
            return self.visit_identity(transformer)
        else:
            raise TypeError('Unknown {}: {}'.format(LinesTransformer,
                                                    str(transformer)))

    def visit_identity(self, transformer: IdentityLinesTransformer):
        raise NotImplementedError('abstract method')

    def visit_sequence(self, transformer: SequenceLinesTransformer):
        raise NotImplementedError('abstract method')

    def visit_custom(self, transformer: CustomLinesTransformer):
        raise NotImplementedError('abstract method')
