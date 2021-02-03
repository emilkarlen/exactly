from typing import Sequence, TypeVar

from exactly_lib.definitions import formatting
from exactly_lib.impls.types.expression import grammar
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

T = TypeVar('T')


def entry(alias_name: str,
          aliased: NameAndValue[grammar.Primitive[T]]) -> NameAndValue[grammar.Primitive[T]]:
    return NameAndValue(
        alias_name,
        grammar.Primitive(
            aliased.value.parse_arguments,
            _Description(aliased.name, aliased.value.description())
        )
    )


class _Description(grammar.PrimitiveDescription):
    def __init__(self,
                 name: str,
                 description: grammar.PrimitiveDescription,
                 ):
        self._name = name
        self._description = description

    def initial_argument(self, name: str) -> a.ArgumentUsage:
        return self._description.initial_argument(name)

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return self._description.argument_usage_list

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'aliased': formatting.keyword(self._name),
        })
        return tp.fnap(_DESCRIPTION)


_DESCRIPTION = """\
An alias for {aliased}.
"""
