import pathlib
from typing import Iterable, Sequence, Tuple

from exactly_lib import program_info
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.doc_format import directory_variable_name_text
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.formatting import program_name
from exactly_lib.test_case_file_structure import tcds_symbols
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.string_transformer.impl.custom import CustomStringTransformer
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformerAdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser

HDS_PATH_WITH_REPLACEMENT_PRECEDENCE = tcds_symbols.SYMBOL_HDS_CASE


class TcdsPathsReplacementStringTransformer(CustomStringTransformer):
    def __init__(self,
                 name: str,
                 tcds: Tcds,
                 ):
        super().__init__(name)
        self._name_and_value_list = _derive_name_and_value_list(tcds)

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return (_replace(self._name_and_value_list, line) for line in lines)


def ddv(name: str) -> StringTransformerDdv:
    return _Ddv(name)


class _Ddv(StringTransformerDdv):
    def __init__(self, name: str):
        self._name = name

    def structure(self) -> StructureRenderer:
        return renderers.header_only(self._name)

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return advs.ConstantAdv(TcdsPathsReplacementStringTransformer(self._name, tcds))


def replace(tcds: Tcds,
            contents: str) -> str:
    name_and_value_list = _derive_name_and_value_list(tcds)
    return _replace(name_and_value_list, contents)


def _replace(name_and_value_list: Iterable[Tuple[str, str]],
             contents: str) -> str:
    for var_name, var_value in name_and_value_list:
        contents = contents.replace(var_value, var_name)
    return contents


def _derive_name_and_value_list(tcds: Tcds) -> iter:
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


def help_section_contents() -> SectionContents:
    text_parser = TextParser({
        'checked_file': 'checked file',
        'program_name': program_info.PROGRAM_NAME,
        'hds_act_symbol': tcds_symbols.SYMBOL_HDS_ACT,
        'hds_case_symbol': tcds_symbols.SYMBOL_HDS_CASE,
        'hds_symbol_with_replacement_precedence': HDS_PATH_WITH_REPLACEMENT_PRECEDENCE,
    })
    prologue = text_parser.fnap(_WITH_REPLACED_TCDS_PATHS_PROLOGUE)
    variables_list = [docs.simple_header_only_list(map(directory_variable_name_text,
                                                       sorted(tcds_symbols.ALL_REPLACED_SYMBOLS)),
                                                   docs.lists.ListType.ITEMIZED_LIST)]
    return SectionContents(prologue + variables_list)


def see_also() -> Sequence[SeeAlsoTarget]:
    return [
        concepts.SYMBOL_CONCEPT_INFO.cross_reference_target,
    ]


SINGLE_LINE_DESCRIPTION = """\
Every occurrence of a string that matches the absolute path of a {TCDS} directory
is replaced with the name of the corresponding {symbol}.
""".format(program_name=program_name(program_info.PROGRAM_NAME),
           TCDS=concepts.TCDS_CONCEPT_INFO.acronym,
           symbol=concepts.SYMBOL_CONCEPT_INFO.singular_name)

_WITH_REPLACED_TCDS_PATHS_PROLOGUE = """\
If {hds_case_symbol} and {hds_act_symbol} are equal, then paths will be replaced with
{hds_symbol_with_replacement_precedence}.


Paths that are replaced:
"""
