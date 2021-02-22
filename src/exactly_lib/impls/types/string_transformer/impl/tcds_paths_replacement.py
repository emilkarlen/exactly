import pathlib
from typing import Iterable, Sequence, Tuple, Iterator

from exactly_lib import program_info
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.doc_format import directory_variable_name_text
from exactly_lib.definitions.entity import all_entity_types
from exactly_lib.definitions.entity import concepts
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.impls.types.string_transformer import sdvs
from exactly_lib.impls.types.string_transformer.impl.sources.transformed_string_sources import \
    StringTransformerFromLinesTransformer
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.tcfs import tcds_symbols
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

HDS_PATH_WITH_REPLACEMENT_PRECEDENCE = tcds_symbols.SYMBOL_HDS_CASE


def parse(token_parser: TokenParser) -> StringTransformerSdv:
    return sdvs.StringTransformerSdvConstantOfDdv(ddv(names.TCDS_PATH_REPLACEMENT))


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'checked_file': 'checked file',
            'program_name': program_info.PROGRAM_NAME,
            'plain_string': misc_texts.PLAIN_STRING,
            'TCDS': concepts.TCDS_CONCEPT_INFO.acronym,
            'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
            'builtin_symbol': all_entity_types.BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.name,
            'hds_act_symbol': tcds_symbols.SYMBOL_HDS_ACT,
            'hds_case_symbol': tcds_symbols.SYMBOL_HDS_CASE,
            'hds_symbol_with_replacement_precedence': HDS_PATH_WITH_REPLACEMENT_PRECEDENCE,
        })
        prologue = tp.fnap(_PROLOGUE)
        epilogue = tp.fnap(_EPILOGUE)
        variables_list = [
            docs.simple_header_only_list(map(directory_variable_name_text,
                                             sorted(tcds_symbols.ALL_REPLACED_SYMBOLS)),
                                         docs.lists.ListType.ITEMIZED_LIST)
        ]
        return prologue + variables_list + epilogue

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [
            concepts.TCDS_CONCEPT_INFO.cross_reference_target,
        ]


class TcdsPathsReplacementStringTransformer(StringTransformerFromLinesTransformer):
    def __init__(self,
                 name: str,
                 tcds: TestCaseDs,
                 ):
        self._name = name
        self._name_and_value_list = _derive_name_and_value_list(tcds)
        self._structure = renderers.header_only(name)

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return self._structure

    def _transformation_may_depend_on_external_resources(self) -> bool:
        return False

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        return (_replace(self._name_and_value_list, line) for line in lines)


def ddv(name: str) -> StringTransformerDdv:
    return _Ddv(name)


class _Ddv(StringTransformerDdv):
    def __init__(self, name: str):
        self._name = name

    def structure(self) -> StructureRenderer:
        return renderers.header_only(self._name)

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
        return advs.ConstantAdv(TcdsPathsReplacementStringTransformer(self._name, tcds))


def replace(tcds: TestCaseDs,
            contents: str) -> str:
    name_and_value_list = _derive_name_and_value_list(tcds)
    return _replace(name_and_value_list, contents)


def _replace(name_and_value_list: Iterable[Tuple[str, str]],
             contents: str) -> str:
    for var_name, var_value in name_and_value_list:
        contents = contents.replace(var_value, var_name)
    return contents


def _derive_name_and_value_list(tcds: TestCaseDs) -> iter:
    hds = tcds.hds
    all_symbols = tcds_symbols.replaced(tcds)
    if hds.case_dir == hds.act_dir:
        return _first_is(HDS_PATH_WITH_REPLACEMENT_PRECEDENCE, all_symbols)
    elif _dir_is_sub_dir_of(hds.case_dir, hds.act_dir):
        return _first_is(tcds_symbols.SYMBOL_HDS_CASE, all_symbols)
    elif _dir_is_sub_dir_of(hds.act_dir, hds.case_dir):
        return _first_is(tcds_symbols.SYMBOL_HDS_ACT, all_symbols)
    else:
        return all_symbols.items()


def _dir_is_sub_dir_of(potential_sub_dir: pathlib.Path, potential_parent_dir: pathlib.Path) -> bool:
    return str(potential_sub_dir).startswith(str(potential_parent_dir))


def _first_is(key_of_first_element: str, all_vars: dict) -> iter:
    value_of_first_element = all_vars.pop(key_of_first_element)
    return [(key_of_first_element, value_of_first_element)] + list(all_vars.items())


_PROLOGUE = """\
Replaces every occurrence of a {plain_string} that equals
the absolute path of a {TCDS} directory
(on a single line)
with the name of the corresponding {builtin_symbol}.


Paths/{symbol:s} that are replaced:
"""

_EPILOGUE = """\
If {hds_case_symbol} and {hds_act_symbol} are equal, then paths will be replaced with
{hds_symbol_with_replacement_precedence}.
"""
