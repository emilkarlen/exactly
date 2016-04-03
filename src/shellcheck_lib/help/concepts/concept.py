from shellcheck_lib.execution.execution_directory_structure import execution_directories
from shellcheck_lib.help.concepts.concept_structure import Name, PlainConceptDocumentation
from shellcheck_lib.help.concepts.configuration_parameters import ALL_CONFIGURATION_PARAMETERS
from shellcheck_lib.help.utils.description import Description
from shellcheck_lib.help.utils.phase_names import CONFIGURATION_PHASE_NAME
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import ParagraphItem
from shellcheck_lib.util.textformat.structure.structures import text, para


class _Sandbox(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('sandbox'))

    def purpose(self) -> Description:
        return Description(text(_SANDBOX_SINGLE_LINE_DESCRIPTION),
                           [directory_structure_list(execution_directories)])


SANDBOX_CONCEPT = _Sandbox()

_SANDBOX_SINGLE_LINE_DESCRIPTION = """\
The temporary directory where test cases are executed."""


def directory_structure_list(dir_with_sub_dir_list: list) -> ParagraphItem:
    items = []
    for dir_wsd in dir_with_sub_dir_list:
        sub_dirs_items = []
        if dir_wsd.sub_dirs:
            sub_dirs_items = [directory_structure_list(dir_wsd.sub_dirs)]
        items.append(lists.HeaderContentListItem(text(dir_wsd.name + '/'), sub_dirs_items))
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST))


class _ConfigurationParameterConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('configuration parameter'))

    def purpose(self) -> Description:
        return Description(text(_CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION.format(CONFIGURATION_PHASE_NAME)),
                           [configuration_parameters_list()])


CONFIGURATION_PARAMETER_CONCEPT = _ConfigurationParameterConcept()

_CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION = """\
Values that are set by the {0} phase and determines how the remaining phases are executed."""


def configuration_parameters_list() -> ParagraphItem:
    all_cps = sorted(ALL_CONFIGURATION_PARAMETERS, key=lambda cd: cd.name().singular)
    items = [lists.HeaderContentListItem(text(cp.name().singular),
                                         [para(cp.purpose().single_line_description)])
             for cp in all_cps]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST))
