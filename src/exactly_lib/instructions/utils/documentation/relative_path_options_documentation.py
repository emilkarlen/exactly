from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.execution import environment_variables as env
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO, \
    HOME_DIRECTORY_CONCEPT_INFO, SANDBOX_CONCEPT_INFO, SYMBOL_CONCEPT_INFO
from exactly_lib.help.concepts.plain_concepts.current_working_directory import CURRENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.help_texts.argument_rendering.path_syntax import SYMBOL_REFERENCE, RELATIVITY_ARGUMENT
from exactly_lib.help_texts.file_ref import REL_SYMBOL_OPTION_NAME
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.instructions.assign_symbol import PATH_TYPE
from exactly_lib.help_texts.test_case.instructions.instruction_names import SYMBOL_DEFINITION_INSTRUCTION_NAME
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.instructions.utils.arg_parse.symbol import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render.cli_program_syntax import ArgumentInArgumentDescriptionRenderer
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs


def default_relativity_for_rel_opt_type(path_arg_name: str,
                                        default_relativity_type: RelOptionType) -> list:
    return docs.paras(_DEFAULT_RELATIVITY
                      .format(path=path_arg_name,
                              default_relativity_location=_ALL[default_relativity_type].relativity_root_description))


def relativity_syntax_element_descriptions(
        path_that_may_be_relative: a.Named,
        rel_options_conf: RelOptionsConfiguration,
        relativity_argument: a.Named = RELATIVITY_ARGUMENT) -> list:
    renderer = RelOptionRenderer(path_that_may_be_relative.name)
    ret_val = [
        SyntaxElementDescription(relativity_argument.name,
                                 [renderer.list_for(rel_options_conf)]),
    ]
    if rel_options_conf.is_rel_symbol_option_accepted:
        ret_val.append(SyntaxElementDescription(SYMBOL_REFERENCE.name,
                                                normalize_and_parse(_SYMBOL_REFERENCE_DESCRIPTION.format(
                                                    symbol_reference=symbol_reference_syntax_for_name('SYMBOL'),
                                                    symbol_name='SYMBOL',
                                                    def_instruction=SYMBOL_DEFINITION_INSTRUCTION_NAME,
                                                ))))
    return ret_val


def see_also_concepts(rel_options_conf: RelOptionsConfiguration) -> list:
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
    if rel_options_conf.is_rel_symbol_option_accepted:
        if SYMBOL_CONCEPT_INFO not in ret_val:
            ret_val.append(SYMBOL_CONCEPT_INFO)
    return ret_val


def add_concepts_if_not_listed(output: list,
                               concepts_to_add: list):
    for concept in concepts_to_add:
        if concept not in output:
            output.append(concept)


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
            'DIR_TMP': sds.PATH__TMP_USER,
            'DIR_ACT': sds.SUB_DIRECTORY__ACT,
            'DIR_RESULT': sds.SUB_DIRECTORY__RESULT,
            'SYMBOL_NAME': _SYMBOL_NAME,
            'PATH_SYMBOL_TYPE': PATH_TYPE,
            'cwd': formatting.concept(CURRENT_WORKING_DIRECTORY_CONCEPT.name().singular),
            'home_directory': formatting.concept(HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'sandbox_concept': formatting.concept(SANDBOX_CONCEPT_INFO.singular_name),
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

    def list_for(self, rel_options_conf: RelOptionsConfiguration) -> lists.HeaderContentList:
        items = []
        for rel_option_type in rel_options_conf.accepted_relativity_variants.rel_option_types:
            items.append(self.item_for(self.option_info_for(rel_option_type)))
        if rel_options_conf.is_rel_symbol_option_accepted:
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
        return lists.HeaderContentListItem(docs.text(self.arg_renderer.visit(_REL_SYMBOL_OPTION)),
                                           self.paragraphs(_REL_SYMBOL_DESCRIPTION))


_REL_TMP_DESCRIPTION = """\
{PATH} is relative the {DIR_TMP}/ directory in the {sandbox_concept}.
"""

_REL_ACT_DESCRIPTION = """\
{PATH} is relative the {DIR_ACT}/ directory in the {sandbox_concept}.
"""

_REL_RESULT_DESCRIPTION = """\
{PATH} is relative the {DIR_RESULT}/ directory in the {sandbox_concept}.
"""

_REL_CWD_DESCRIPTION = """\
{PATH} is relative the {cwd}.
"""

_REL_HOME_DESCRIPTION = """\
{PATH} is relative the {home_directory}.
"""

_REL_SYMBOL_DESCRIPTION = """\
{PATH} is relative the path denoted by the symbol {SYMBOL_NAME}
(which must have been defined as a {PATH_SYMBOL_TYPE} symbol).
"""

_ALL = {
    RelOptionType.REL_TMP: _RelOptionTypeInfo(file_ref_texts.REL_TMP_OPTION_NAME,
                                              env.ENV_VAR_TMP,
                                              _REL_TMP_DESCRIPTION,
                                              [SANDBOX_CONCEPT_INFO],
                                              ),
    RelOptionType.REL_ACT: _RelOptionTypeInfo(file_ref_texts.REL_ACT_OPTION_NAME,
                                              env.ENV_VAR_ACT,
                                              _REL_ACT_DESCRIPTION,
                                              [SANDBOX_CONCEPT_INFO]),
    RelOptionType.REL_RESULT: _RelOptionTypeInfo(file_ref_texts.REL_RESULT_OPTION_NAME,
                                                 env.ENV_VAR_RESULT,
                                                 _REL_RESULT_DESCRIPTION,
                                                 [SANDBOX_CONCEPT_INFO]),
    RelOptionType.REL_CWD: _RelOptionTypeInfo(file_ref_texts.REL_CWD_OPTION_NAME,
                                              formatting.concept(
                                                  CURRENT_WORKING_DIRECTORY_CONCEPT_INFO.singular_name),
                                              _REL_CWD_DESCRIPTION,
                                              [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO]),
    RelOptionType.REL_HOME: _RelOptionTypeInfo(file_ref_texts.REL_HOME_OPTION_NAME,
                                               formatting.concept(
                                                   HOME_DIRECTORY_CONCEPT_INFO.singular_name),
                                               _REL_HOME_DESCRIPTION,
                                               [HOME_DIRECTORY_CONCEPT_INFO]),
}

_DEFAULT_RELATIVITY = """\
By default, {path} is relative the {default_relativity_location}.
"""

_SYMBOL_NAME = 'SYMBOL'

_REL_SYMBOL_OPTION = a.Option(REL_SYMBOL_OPTION_NAME, _SYMBOL_NAME)

_SYMBOL_REFERENCE_DESCRIPTION = """\
A reference to a symbol {symbol_name} using the syntax

{symbol_reference}


The symbol must have been defined using the {def_instruction} instruction.
"""
