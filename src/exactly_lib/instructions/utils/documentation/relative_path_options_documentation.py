from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts import test_case_file_structure as tc_fs
from exactly_lib.help_texts.entity import concepts as ci, syntax_element
from exactly_lib.help_texts.entity import conf_params
from exactly_lib.help_texts.entity.types import PATH_TYPE_INFO
from exactly_lib.help_texts.names import formatting
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants, \
    RelSdsOptionType, RelHomeOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_SDS_OPTIONS_MAP, REL_HOME_OPTIONS_MAP, \
    REL_CWD_INFO
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render.cli_program_syntax import ArgumentInArgumentDescriptionRenderer
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser
from exactly_lib.util.textformat.utils import transform_list_to_table


def default_relativity_for_rel_opt_type(path_arg_name: str,
                                        default_relativity_type: RelOptionType) -> list:
    return docs.paras(_DEFAULT_RELATIVITY
                      .format(path=path_arg_name,
                              default_relativity_location=_ALL[default_relativity_type].relativity_root_description))


def relativity_syntax_element_descriptions(
        path_that_may_be_relative: a.Named,
        rel_options_conf: RelOptionsConfiguration,
        relativity_argument: a.Named = instruction_arguments.RELATIVITY_ARGUMENT) -> list:
    return [
        relativity_syntax_element_description(path_that_may_be_relative,
                                              rel_options_conf,
                                              relativity_argument)
    ]


def relativity_syntax_element_description(
        path_that_may_be_relative: a.Named,
        rel_options_conf: RelOptionsConfiguration,
        relativity_argument: a.Named = instruction_arguments.RELATIVITY_ARGUMENT) -> SyntaxElementDescription:
    renderer = RelOptionRenderer(path_that_may_be_relative.name)
    return SyntaxElementDescription(
        relativity_argument.name,
        [transform_list_to_table(renderer.list_for(rel_options_conf.accepted_relativity_variants))])


def relativity_options_paragraph(path_that_may_be_relative: str,
                                 variants: PathRelativityVariants) -> ParagraphItem:
    renderer = RelOptionRenderer(path_that_may_be_relative)
    return transform_list_to_table(renderer.list_for(variants))


def see_also_name_and_cross_refs(rel_options_conf: RelOptionsConfiguration) -> list:
    """
    :rtype: [`SingularAndPluralNameAndCrossReferenceId`]
    """
    relativity_variants = rel_options_conf.accepted_relativity_variants
    ret_val = []
    for rel_option_type in relativity_variants.rel_option_types:
        concepts_for_type = _ALL[rel_option_type].see_also
        for concept in concepts_for_type:
            if concept not in ret_val:
                ret_val.append(concept)
    if ci.SYMBOL_CONCEPT_INFO not in ret_val:
        ret_val.append(ci.SYMBOL_CONCEPT_INFO)
    return ret_val


class _RelOptionInfo(tuple):
    def __new__(cls,
                name: a.Option,
                paragraph_items: list,
                see_also: iter = ()):
        """
        :type paragraph_items: [`ParagraphItem`]
        :type see_also:
        """
        return tuple.__new__(cls, (name, paragraph_items, list(see_also)))

    @property
    def option(self) -> a.Option:
        return self[0]

    @property
    def paragraph_items(self) -> list:
        return self[1]

    @property
    def see_also(self) -> list:
        return self[2]


class _RelOptionTypeInfo(tuple):
    def __new__(cls,
                name: a.OptionName,
                relativity_root_description: str,
                paragraph_items_text: str,
                see_also: list):
        """
        :type see_also: [`ConceptDocumentation`]
        """
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
    def see_also(self) -> list:
        return self[2]

    @property
    def relativity_root_description(self) -> str:
        return self[3]


class RelOptionRenderer:
    def __init__(self,
                 path_name_in_description: str,
                 argument_name: str = None):
        self.argument_name = argument_name
        self.parser = TextParser({
            'PATH': path_name_in_description,
            'DIR_TMP': formatting.concept(tc_fs.SDS_TMP_INFO.informative_name),
            'DIR_ACT': formatting.concept(tc_fs.SDS_ACT_INFO.informative_name),
            'DIR_RESULT': formatting.concept(tc_fs.SDS_RESULT_INFO.informative_name),
            'SYMBOL_NAME': syntax_element.SYMBOL_NAME_SYNTAX_ELEMENT.argument.name,
            'PATH_SYMBOL_TYPE': PATH_TYPE_INFO.identifier,
            'cwd': formatting.concept_(ci.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'home_case_directory': formatting.conf_param_(conf_params.HOME_CASE_DIRECTORY_CONF_PARAM_INFO),
            'home_act_directory': formatting.conf_param_(conf_params.HOME_ACT_DIRECTORY_CONF_PARAM_INFO),
            'sandbox_concept': formatting.concept_(ci.SANDBOX_CONCEPT_INFO),
        })
        self.arg_renderer = ArgumentInArgumentDescriptionRenderer()

    def paragraphs(self, s: str) -> list:
        return self.parser.fnap(s)

    def option_info(self,
                    option_type_info: _RelOptionTypeInfo) -> _RelOptionInfo:
        return _RelOptionInfo(a.Option(option_type_info.option_name,
                                       argument=self.argument_name),
                              self.paragraphs(option_type_info.paragraph_items_text),
                              option_type_info.see_also)

    def list_for(self, variants: PathRelativityVariants) -> lists.HeaderContentList:
        items = []
        for rel_option_type in _DISPLAY_ORDER:
            if rel_option_type in variants.rel_option_types:
                items.append(self.item_for(self.option_info_for(rel_option_type)))
        items.append(self._rel_symbol_item())
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS))

    def item_for(self, info: _RelOptionInfo) -> lists.HeaderContentListItem:
        return lists.HeaderContentListItem(docs.text(self.arg_renderer.visit(info.option)),
                                           info.paragraph_items)

    def option_info_for(self, option_type: RelOptionType) -> _RelOptionInfo:
        return self.option_info(_ALL[option_type])

    def _rel_symbol_item(self) -> lists.HeaderContentListItem:
        return lists.HeaderContentListItem(docs.text(self.arg_renderer.visit(instruction_arguments.REL_SYMBOL_OPTION)),
                                           self.paragraphs(_REL_SYMBOL_DESCRIPTION))


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

_REL_HOME_CASE_DESCRIPTION = """\
{PATH} is relative the {home_case_directory}.
"""

_REL_HOME_ACT_DESCRIPTION = """\
{PATH} is relative the {home_act_directory}.
"""

_REL_SYMBOL_DESCRIPTION = """\
{PATH} is relative the path denoted by the symbol {SYMBOL_NAME}
(which must have been defined as a {PATH_SYMBOL_TYPE} symbol).
"""

_DISPLAY_ORDER = (
    RelOptionType.REL_HOME_CASE,
    RelOptionType.REL_HOME_ACT,
    RelOptionType.REL_ACT,
    RelOptionType.REL_TMP,
    RelOptionType.REL_RESULT,
    RelOptionType.REL_CWD,
)


def _rel_sds(rel: RelSdsOptionType,
             description: str) -> _RelOptionTypeInfo:
    ri = REL_SDS_OPTIONS_MAP[rel]

    return _RelOptionTypeInfo(ri.option_name,
                              ri.directory_variable_name,
                              description,
                              [ci.SANDBOX_CONCEPT_INFO],
                              )


def _rel_hds(rel: RelHomeOptionType,
             description: str) -> _RelOptionTypeInfo:
    ri = REL_HOME_OPTIONS_MAP[rel]

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

    RelOptionType.REL_HOME_CASE: _rel_hds(RelHomeOptionType.REL_HOME_CASE,
                                          _REL_HOME_CASE_DESCRIPTION),

    RelOptionType.REL_HOME_ACT: _rel_hds(RelHomeOptionType.REL_HOME_ACT,
                                         _REL_HOME_ACT_DESCRIPTION),
}

_DEFAULT_RELATIVITY = """\
By default, {path} is relative the {default_relativity_location}.
"""
