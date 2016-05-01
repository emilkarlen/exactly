from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.execution import execution_directory_structure as sds
from exactly_lib.execution.environment_variables import ENV_VAR_RESULT, ENV_VAR_ACT
from exactly_lib.help.concepts.concept_structure import PlainConceptDocumentation, Name
from exactly_lib.help.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help.utils.description import Description
from exactly_lib.help.utils.formatting import AnyInstructionNameDictionary
from exactly_lib.help.utils.phase_names import phase_name_dictionary, SETUP_PHASE_NAME
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import text, SEPARATION_OF_HEADER_AND_CONTENTS, \
    simple_header_only_list, paras


class _Sandbox(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('sandbox', 'sandboxes'))

    def purpose(self) -> Description:
        phase = phase_name_dictionary()
        instruction = AnyInstructionNameDictionary()
        rest_paragraphs = []
        rest_paragraphs.extend(normalize_and_parse(_SANDBOX_PRE_DIRECTORY_TREE.format(phase=phase)))
        rest_paragraphs.append(directory_structure_list(sds.execution_directories))
        rest_paragraphs.extend(sandbox_directories_info_header())
        rest_paragraphs.append(sandbox_directories_info(phase, instruction))
        return Description(text(_SANDBOX_SINGLE_LINE_DESCRIPTION),
                           rest_paragraphs)

    def see_also(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(SETUP_PHASE_NAME.plain,
                                                   CHANGE_DIR_INSTRUCTION_NAME),
        ]


SANDBOX_CONCEPT = _Sandbox()
_SANDBOX_SINGLE_LINE_DESCRIPTION = """\
The temporary directory structure where a test case is executed."""
_SANDBOX_PRE_DIRECTORY_TREE = """\
Every test case uses its own sandbox.


The sandbox is created just before the {phase[setup]} phase is executed.


It consists of the following directory tree:
"""


def sandbox_directories_info_header() -> list:
    return paras('Description:')


def sandbox_directories_info(phase_name_dictionary: dict,
                             instruction: AnyInstructionNameDictionary) -> ParagraphItem:
    items = []
    items.append(lists.HeaderContentListItem(
        text('%s/' % sds.SUB_DIRECTORY__ACT),
        _act_dir_description_paragraphs(instruction, phase_name_dictionary)))
    items.append(lists.HeaderContentListItem(
        text('%s/' % sds.SUB_DIRECTORY__RESULT),
        _result_dir_description_paragraphs(instruction, phase_name_dictionary)))
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))


def _act_dir_description_paragraphs(instruction: AnyInstructionNameDictionary, phase: dict):
    ret_val = []
    ret_val.extend(normalize_and_parse(
        _ACT_DIR_DESCRIPTION.format(phase=phase,
                                    instruction=instruction)))
    ret_val.extend(_act_dir_environment_variables(phase=phase))
    return ret_val


def _result_dir_description_paragraphs(instruction: AnyInstructionNameDictionary, phase: dict):
    ret_val = []
    ret_val.extend(normalize_and_parse(
        _RESULT_DIR_DESCRIPTION.format(phase=phase,
                                       instruction=instruction)))
    ret_val.append(simple_header_only_list(sds.RESULT_FILE_ALL,
                                           lists.ListType.VARIABLE_LIST))
    ret_val.extend(_result_dir_environment_variables(phase))
    return ret_val


_ACT_DIR_DESCRIPTION = """\
This directory is the Present Working Directory (PWD) when the {phase[setup]} phase begin.


If it is not changed, it will also be the PWD for the {phase[act]} phase (hence its name).


(Files and directories that {phase[setup]:syntax} creates
are installed into the PWD, if no instruction options are used to change this.)
"""
_RESULT_DIR_DESCRIPTION = """\
This directory is initially empty.

It is populated when the {phase[act]} phase is executed
with the following files (with obvious contents):
"""


def _result_dir_environment_variables(phase: dict) -> list:
    return paras('{env_var}: The value of this environment variable is the absolute path of this directory '
                 '(after the {phase[act]} phase has been executed).'
                 .format(phase=phase,
                         env_var=ENV_VAR_RESULT))


def _act_dir_environment_variables(phase: dict) -> list:
    return paras('{env_var}: The value of this environment variable is the absolute path of this directory.'
                 .format(phase=phase,
                         env_var=ENV_VAR_ACT))


def directory_structure_list(dir_with_sub_dir_list: list) -> ParagraphItem:
    items = []
    for dir_wsd in sorted(dir_with_sub_dir_list, key=lambda x: x.name):
        sub_dirs_items = []
        if dir_wsd.sub_dirs:
            sub_dirs_items = [directory_structure_list(dir_wsd.sub_dirs)]
        items.append(lists.HeaderContentListItem(text(dir_wsd.name + '/'), sub_dirs_items))
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST))
