from exactly_lib.execution import environment_variables as env
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.textformat_parse import TextParser
from exactly_lib.instructions.utils import relative_path_options as options
from exactly_lib.instructions.utils.relative_path_options import RelOptionType
from exactly_lib.util.cli_syntax.elements.argument import OptionName, Option
from exactly_lib.util.cli_syntax.render.cli_program_syntax import ArgumentInArgumentDescriptionRenderer
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs


class RelOptionInfo(tuple):
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
                    name: OptionName,
                    description: str,
                    see_also: list = ()) -> RelOptionInfo:
        return RelOptionInfo(Option(name,
                                    argument=self.argument_name),
                             self.paragraphs(description),
                             see_also)

    def list_for(self, rel_option_types: list) -> lists.HeaderContentList:
        items = []
        for rel_option_type in rel_option_types:
            items.append(self.item_for(self.option_info_for(rel_option_type)))
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_separations=docs.SEPARATION_OF_HEADER_AND_CONTENTS))

    def item_for(self, info: RelOptionInfo) -> lists.HeaderContentListItem:
        return lists.HeaderContentListItem(docs.text(self.arg_renderer.visit(info.option)),
                                           info.paragraph_items)

    def option_info_for(self, option_type: RelOptionType) -> RelOptionInfo:
        name, see_also, desc_text = _ALL[option_type]
        return self.option_info(name, desc_text, see_also)


_REL_TMP_DESCRIPTION = """\
{PATH} is relative the {ENV_VAR_TMP}.
"""

_REL_ACT_DESCRIPTION = """\
{PATH} is relative the {ENV_VAR_ACT}.
"""

_REL_PWD_DESCRIPTION = """\
{PATH} is relative the {pwd}.
"""

_REL_HOME_DESCRIPTION = """\
{PATH} is relative the {home_directory}.
"""

_ALL = {
    RelOptionType.REL_TMP: (options.REL_TMP_OPTION_NAME,
                            [],
                            _REL_TMP_DESCRIPTION),
    RelOptionType.REL_ACT: (options.REL_ACT_OPTION_NAME,
                            [],
                            _REL_ACT_DESCRIPTION),
    RelOptionType.REL_PWD: (options.REL_CWD_OPTION_NAME,
                            [PRESENT_WORKING_DIRECTORY_CONCEPT.cross_reference_target()],
                            _REL_PWD_DESCRIPTION),
    RelOptionType.REL_HOME: (options.REL_HOME_OPTION_NAME,
                             [HOME_DIRECTORY_CONFIGURATION_PARAMETER.cross_reference_target()],
                             _REL_HOME_DESCRIPTION),
}
