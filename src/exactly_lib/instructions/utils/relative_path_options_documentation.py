from exactly_lib.common.instruction_documentation import SyntaxElementDescription
from exactly_lib.execution import environment_variables as env
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.environment_variable import ENVIRONMENT_VARIABLE_CONCEPT
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.textformat_parse import TextParser
from exactly_lib.instructions.utils import relative_path_options as options
from exactly_lib.instructions.utils.relative_path_options import RelOptionType
from exactly_lib.util.cli_syntax.elements.argument import OptionName, Option, Named
from exactly_lib.util.cli_syntax.render.cli_program_syntax import ArgumentInArgumentDescriptionRenderer
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs

RELATIVITY_ARGUMENT = Named('RELATIVITY')


def default_relativity_for_rel_opt_type(path_arg_name: str,
                                        default_relativity_type: options.RelOptionType) -> list:
    return docs.paras(_DEFAULT_RELATIVITY
                      .format(path=path_arg_name,
                              default_relativity_location=_ALL[default_relativity_type].relativity_root_description))


def relativity_syntax_element_description(path_that_may_be_relative: Named,
                                          iter_of_rel_option_type: iter,
                                          relativity_argument: Named = RELATIVITY_ARGUMENT) -> SyntaxElementDescription:
    renderer = RelOptionRenderer(path_that_may_be_relative.name)
    return SyntaxElementDescription(relativity_argument.name,
                                    [renderer.list_for(iter_of_rel_option_type)])


def see_also_concepts(iter_of_rel_option_type: iter) -> list:
    """
    :rtype: [`ConceptDocumentation`]
    """
    ret_val = []
    for rel_option_type in iter_of_rel_option_type:
        concepts_for_type = _ALL[rel_option_type].see_also
        for concept in concepts_for_type:
            if concept not in ret_val:
                ret_val.append(concept)
    return ret_val


class _RelOptionInfo(tuple):
    def __new__(cls,
                name: Option,
                paragraph_items: list,
                see_also: iter = ()):
        """
        :type paragraph_items: [`ParagraphItem`]
        :type see_also:
        """
        return tuple.__new__(cls, (name, paragraph_items, list(see_also)))

    @property
    def option(self) -> Option:
        return self[0]

    @property
    def paragraph_items(self) -> list:
        return self[1]

    @property
    def see_also(self) -> list:
        return self[2]


class _RelOptionTypeInfo(tuple):
    def __new__(cls,
                name: OptionName,
                relativity_root_description: str,
                paragraph_items_text: str,
                see_also: list):
        """
        :type see_also: [`ConceptDocumentation`]
        """
        return tuple.__new__(cls, (name, paragraph_items_text, see_also, relativity_root_description))

    @property
    def option_name(self) -> OptionName:
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
            'ENV_VAR_TMP': env.ENV_VAR_TMP,
            'ENV_VAR_ACT': env.ENV_VAR_ACT,
            'pwd': formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular),
            'home_directory': formatting.concept(HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
        })
        self.arg_renderer = ArgumentInArgumentDescriptionRenderer()

    def paragraphs(self, s: str) -> list:
        return self.parser.fnap(s)

    def option_info(self,
                    option_type_info: _RelOptionTypeInfo) -> _RelOptionInfo:
        return _RelOptionInfo(Option(option_type_info.option_name,
                                     argument=self.argument_name),
                              self.paragraphs(option_type_info.paragraph_items_text),
                              option_type_info.see_also)

    def list_for(self, rel_option_types: list) -> lists.HeaderContentList:
        items = []
        for rel_option_type in rel_option_types:
            items.append(self.item_for(self.option_info_for(rel_option_type)))
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS))

    def item_for(self, info: _RelOptionInfo) -> lists.HeaderContentListItem:
        return lists.HeaderContentListItem(docs.text(self.arg_renderer.visit(info.option)),
                                           info.paragraph_items)

    def option_info_for(self, option_type: RelOptionType) -> _RelOptionInfo:
        return self.option_info(_ALL[option_type])


_REL_TMP_DESCRIPTION = """\
{PATH} is relative the {ENV_VAR_TMP} directory.
"""

_REL_ACT_DESCRIPTION = """\
{PATH} is relative the {ENV_VAR_ACT} directory.
"""

_REL_PWD_DESCRIPTION = """\
{PATH} is relative the {pwd}.
"""

_REL_HOME_DESCRIPTION = """\
{PATH} is relative the {home_directory}.
"""

_ALL = {
    RelOptionType.REL_TMP: _RelOptionTypeInfo(options.REL_TMP_OPTION_NAME,
                                              env.ENV_VAR_TMP,
                                              _REL_TMP_DESCRIPTION,
                                              [ENVIRONMENT_VARIABLE_CONCEPT],
                                              ),
    RelOptionType.REL_ACT: _RelOptionTypeInfo(options.REL_ACT_OPTION_NAME,
                                              env.ENV_VAR_ACT,
                                              _REL_ACT_DESCRIPTION,
                                              [ENVIRONMENT_VARIABLE_CONCEPT]),
    RelOptionType.REL_PWD: _RelOptionTypeInfo(options.REL_CWD_OPTION_NAME,
                                              formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular),
                                              _REL_PWD_DESCRIPTION,
                                              [PRESENT_WORKING_DIRECTORY_CONCEPT]),
    RelOptionType.REL_HOME: _RelOptionTypeInfo(options.REL_HOME_OPTION_NAME,
                                               formatting.concept(
                                                   HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
                                               _REL_HOME_DESCRIPTION,
                                               [HOME_DIRECTORY_CONFIGURATION_PARAMETER]),
}

_DEFAULT_RELATIVITY = """\
By default, {path} is relative the {default_relativity_location}.
"""
