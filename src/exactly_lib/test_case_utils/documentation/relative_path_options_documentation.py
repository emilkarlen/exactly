from typing import Sequence, List

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.common.help.with_see_also_set import SyntaxElementDescriptionTree, SyntaxElementDescriptionTreeFromSed
from exactly_lib.definitions import formatting, instruction_arguments
from exactly_lib.definitions import path
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity import concepts as ci, syntax_elements
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants, \
    RelSdsOptionType, RelHdsOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_SDS_OPTIONS_MAP, REL_HDS_OPTIONS_MAP, \
    REL_CWD_INFO, REL_OPTIONS_MAP
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionsConfiguration, \
    RelOptionArgumentConfiguration
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render.cli_program_syntax import render_argument
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.utils import transform_list_to_table


def path_element(path_arg_name: str,
                 rel_options_conf: RelOptionsConfiguration,
                 custom_paragraphs_before: Sequence[ParagraphItem] = (),
                 custom_paragraphs_after: Sequence[ParagraphItem] = ()) -> SyntaxElementDescription:
    return _path_element_description(path_arg_name,
                                     rel_options_conf.default_option,
                                     RelOptionRenderer().sparse_list_for(rel_options_conf.accepted_relativity_variants),
                                     custom_paragraphs_before,
                                     custom_paragraphs_after)


def path_element_relativity_paragraphs(rel_options_conf: RelOptionsConfiguration,
                                       custom_paragraphs_before: Sequence[ParagraphItem] = (),
                                       custom_paragraphs_after: Sequence[ParagraphItem] = (),
                                       ) -> Sequence[ParagraphItem]:
    return _path_element_relativity_paragraphs(rel_options_conf.default_option,
                                               RelOptionRenderer().sparse_list_for(
                                                   rel_options_conf.accepted_relativity_variants),
                                               custom_paragraphs_before,
                                               custom_paragraphs_after)


def path_element_with_all_relativities(path_arg_name: str,
                                       default_relativity: RelOptionType,
                                       custom_paragraphs_after: Sequence[ParagraphItem]) -> SyntaxElementDescription:
    return _path_element_description(path_arg_name,
                                     default_relativity,
                                     RelOptionRenderer().all_options_list(),
                                     [],
                                     custom_paragraphs_after)


def _path_element_description(path_arg_name: str,
                              default_relativity: RelOptionType,
                              options_list: lists.HeaderContentList,
                              custom_paragraphs_before: Sequence[ParagraphItem],
                              custom_paragraphs_after: Sequence[ParagraphItem]) -> SyntaxElementDescription:
    return SyntaxElementDescription(path_arg_name,
                                    _path_element_relativity_paragraphs(default_relativity,
                                                                        options_list,
                                                                        custom_paragraphs_before,
                                                                        custom_paragraphs_after))


def _path_element_relativity_paragraphs(default_relativity: RelOptionType,
                                        options_list: lists.HeaderContentList,
                                        custom_paragraphs_before: Sequence[ParagraphItem],
                                        custom_paragraphs_after: Sequence[ParagraphItem]) -> Sequence[ParagraphItem]:
    ret_val = []
    ret_val += custom_paragraphs_before
    ret_val += [
        docs.para('Accepted relativities (default is "{}"):'.format(
            REL_OPTIONS_MAP[default_relativity].informative_name
        )),
        transform_list_to_table(options_list),
    ]
    ret_val += custom_paragraphs_after

    return ret_val


def path_element_2(rel_options_conf: RelOptionArgumentConfiguration,
                   custom_paragraphs: Sequence[ParagraphItem] = ()) -> SyntaxElementDescription:
    return path_element(rel_options_conf.argument_syntax_name,
                        rel_options_conf.options,
                        custom_paragraphs)


def path_element_3(rel_options_conf: RelOptionArgumentConfiguration,
                   custom_paragraphs: Sequence[ParagraphItem] = ()) -> SyntaxElementDescriptionTree:
    return SyntaxElementDescriptionTreeFromSed(a.Named(rel_options_conf.argument_syntax_name),
                                               path_element_2(rel_options_conf, custom_paragraphs))


def path_elements(path_arg_name: str,
                  rel_options_conf: RelOptionsConfiguration,
                  custom_paragraphs: Sequence[ParagraphItem] = ()) -> List[SyntaxElementDescription]:
    return [
        path_element(path_arg_name, rel_options_conf, custom_paragraphs)
    ]


def sparse_relativity_options_paragraph(variants: PathRelativityVariants) -> ParagraphItem:
    renderer = RelOptionRenderer()
    return transform_list_to_table(renderer.sparse_list_for(variants))


def see_also_name_and_cross_refs(rel_options_conf: RelOptionsConfiguration
                                 ) -> List[SingularNameAndCrossReferenceId]:
    return [
        syntax_elements.PATH_SYNTAX_ELEMENT,
    ]


class _RelOptionTypeInfo(tuple):
    def __new__(cls,
                name: a.OptionName,
                relativity_root_description: str,
                paragraph_items_text: str,
                see_also: List[SingularNameAndCrossReferenceId]):
        return tuple.__new__(cls, (name,
                                   paragraph_items_text,
                                   see_also,
                                   relativity_root_description))

    @property
    def option_name(self) -> a.OptionName:
        return self[0]

    @property
    def paragraph_items_text(self) -> str:
        return self[1]

    @property
    def see_also(self) -> List[SingularNameAndCrossReferenceId]:
        return self[2]

    @property
    def relativity_root_description(self) -> str:
        return self[3]


class RelOptionRenderer:
    def all_options_list(self) -> lists.HeaderContentList:
        items = []
        for rel_option_type in path.DIR_DISPLAY_ORDER:
            items.append(self.sparse_item_for(rel_option_type))
        items += self.special_symbols()
        return self.list_for_items(items)

    def sparse_list_for(self, variants: PathRelativityVariants) -> lists.HeaderContentList:
        items = []
        for rel_option_type in path.sort_rel_options(variants.rel_option_types):
            items.append(self.sparse_item_for(rel_option_type))
        return self.list_for_items(items)

    def sparse_item_for(self, rel_option_type: RelOptionType) -> lists.HeaderContentListItem:
        opt_info = REL_OPTIONS_MAP[rel_option_type]
        return self.item_for(option_syntax.option_syntax(opt_info.option_name),
                             opt_info.informative_name)

    def special_symbols(self) -> List[lists.HeaderContentListItem]:
        return [
            self.item_for(render_argument(instruction_arguments.REL_SYMBOL_OPTION),
                          path.RELATIVITY_DESCRIPTION_SYMBOL),

            self.item_for(path.REL_source_file_dir_OPTION,
                          path.RELATIVITY_DESCRIPTION_SOURCE_FILE),
        ]

    @staticmethod
    def item_for(syntax: str, description: str) -> lists.HeaderContentListItem:
        return docs.list_item(syntax_text(syntax),
                              docs.paras(description))

    @staticmethod
    def list_for_items(items):
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS))


_REL_TMP_DESCRIPTION = """\
{PATH} is relative the {DIR_TMP} in the {sandbox_concept}.
"""

_REL_ACT_DESCRIPTION = """\
{PATH} is relative the {DIR_ACT} in the {sandbox_concept}.
"""

_REL_RESULT_DESCRIPTION = """\
{PATH} is relative the {DIR_RESULT} in the {sandbox_concept}.
"""

_REL_CWD_DESCRIPTION = """\
{PATH} is relative the {cwd}.
"""

_REL_HDS_CASE_DESCRIPTION = """\
{PATH} is relative the {home_case_directory}.
"""

_REL_HDS_ACT_DESCRIPTION = """\
{PATH} is relative the {home_act_directory}.
"""


def _rel_sds(rel: RelSdsOptionType,
             description: str) -> _RelOptionTypeInfo:
    ri = REL_SDS_OPTIONS_MAP[rel]

    return _RelOptionTypeInfo(ri.option_name,
                              ri.directory_name,
                              description,
                              [ci.SDS_CONCEPT_INFO],
                              )


def _rel_hds(rel: RelHdsOptionType,
             description: str) -> _RelOptionTypeInfo:
    ri = REL_HDS_OPTIONS_MAP[rel]

    return _RelOptionTypeInfo(ri.option_name,
                              formatting.concept_(ri.conf_param_info),
                              description,
                              [ri.conf_param_info],
                              )


_ALL = {
    RelOptionType.REL_TMP: _rel_sds(RelSdsOptionType.REL_TMP,
                                    _REL_TMP_DESCRIPTION),

    RelOptionType.REL_ACT: _rel_sds(RelSdsOptionType.REL_ACT,
                                    _REL_ACT_DESCRIPTION),

    RelOptionType.REL_RESULT: _rel_sds(RelSdsOptionType.REL_RESULT,
                                       _REL_RESULT_DESCRIPTION),

    RelOptionType.REL_CWD: _RelOptionTypeInfo(REL_CWD_INFO.option_name,
                                              formatting.concept_(REL_CWD_INFO.cross_ref_info),
                                              _REL_CWD_DESCRIPTION,
                                              [REL_CWD_INFO.cross_ref_info]),

    RelOptionType.REL_HDS_CASE: _rel_hds(RelHdsOptionType.REL_HDS_CASE,
                                         _REL_HDS_CASE_DESCRIPTION),

    RelOptionType.REL_HDS_ACT: _rel_hds(RelHdsOptionType.REL_HDS_ACT,
                                        _REL_HDS_ACT_DESCRIPTION),
}

_DEFAULT_RELATIVITY = """\
By default, {path} is relative the {default_relativity_location}.
"""
