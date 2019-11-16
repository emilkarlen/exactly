import functools
from abc import ABC, abstractmethod
from typing import Iterable, Sequence

from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator, \
    constant_success_validator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription, \
    WithTreeStructureDescription, StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.functional import compose_first_and_second

StringTransformerModel = Iterable[str]


class StringTransformer(WithNameAndTreeStructureDescription, ABC):
    """
    Transforms a sequence of lines, where each line is a string.
    """

    @property
    def is_identity_transformer(self) -> bool:
        """
        Tells if this transformer is the identity transformer
        """
        return False

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        raise NotImplementedError('abstract method')

    def __str__(self):
        return type(self).__name__


class StringTransformerDdv(DirDependentValue[StringTransformer],
                           WithTreeStructureDescription,
                           ABC):

    def structure(self) -> StructureRenderer:
        return renderers.header_only('string transformer TODO')

    def validator(self) -> PreOrPostSdsValueValidator:
        return constant_success_validator()

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformer:
        pass


class IdentityStringTransformer(StringTransformer):
    @property
    def name(self) -> str:
        return 'identity'

    @property
    def is_identity_transformer(self) -> bool:
        return True

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return lines


class SequenceStringTransformer(StringTransformer):
    def __init__(self, transformers: Sequence[StringTransformer]):
        self._transformers = tuple(transformers)

    @property
    def name(self) -> str:
        return 'sequence'

    @property
    def is_identity_transformer(self) -> bool:
        return all([t.is_identity_transformer for t in self._transformers])

    @property
    def transformers(self) -> Sequence[StringTransformer]:
        return self._transformers

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        if not self._transformers:
            return lines
        else:
            return self._sequenced_transformers()(lines)

    def _sequenced_transformers(self):
        lines_to_lines_transformers = [t.transform
                                       for t in self._transformers]

        return functools.reduce(compose_first_and_second, lines_to_lines_transformers)

    def __str__(self):
        return '{}[{}]'.format(type(self).__name__,
                               ','.join(map(str, self._transformers)))


class CustomStringTransformer(StringTransformer, ABC):
    """
    Base class for built in custom transformers.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __str__(self):
        return str(type(self))
