from typing import Sequence

from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.argument_rendering.cl_syntax import arg_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem


class InvokationVariant(tuple):
    def __new__(cls,
                syntax: str,
                description_rest: Sequence[ParagraphItem] = None):
        return tuple.__new__(cls, (syntax, [] if description_rest is None else description_rest))

    @property
    def syntax(self) -> str:
        return self[0]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self[1]


def invokation_variant_from_string(syntax: str,
                                   description_rest: Sequence[ParagraphItem] = None) -> InvokationVariant:
    return InvokationVariant(syntax,
                             description_rest)


def invokation_variant_from_args(argument_usages: Sequence[a.ArgumentUsage],
                                 description_rest: Sequence[ParagraphItem] = None) -> InvokationVariant:
    return InvokationVariant(cl_syntax.cl_syntax_for_args(argument_usages),
                             description_rest)


class SyntaxElementDescription(tuple):
    def __new__(cls,
                element_name: str,
                before_invokation_variants: Sequence[ParagraphItem],
                invokation_variants: Sequence[InvokationVariant] = (),
                after_invokation_variants: Sequence[ParagraphItem] = (),
                ):
        return tuple.__new__(cls, (element_name,
                                   before_invokation_variants,
                                   invokation_variants,
                                   after_invokation_variants))

    @property
    def element_name(self) -> str:
        return self[0]

    @property
    def before_invokation_variants(self) -> Sequence[ParagraphItem]:
        return self[1]

    @property
    def invokation_variants(self) -> Sequence[InvokationVariant]:
        return self[2]

    @property
    def after_invokation_variants(self) -> Sequence[ParagraphItem]:
        return self[3]


def cli_argument_syntax_element_description(argument: a.Argument,
                                            before_invokation_variants: Sequence[ParagraphItem],
                                            invokation_variants: Sequence[InvokationVariant] = (),
                                            after_invokation_variants: Sequence[ParagraphItem] = (),
                                            ) -> SyntaxElementDescription:
    return SyntaxElementDescription(arg_syntax(argument),
                                    before_invokation_variants,
                                    invokation_variants,
                                    after_invokation_variants)
