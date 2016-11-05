from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.execution.environment_variables import ENV_VAR_RESULT, ENV_VAR_ACT
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation, Name
from exactly_lib.help.concepts.some_concept_names import PRESENT_WORKING_DIRECTORY_CONCEPT_NAME
from exactly_lib.help.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.formatting import AnyInstructionNameDictionary
from exactly_lib.help.utils.phase_names import phase_name_dictionary, SETUP_PHASE_NAME
from exactly_lib.test_case import sandbox_directory_structure as sds
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents, Section


class _Sandbox(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('sandbox', 'sandboxes'))

    def purpose(self) -> DescriptionWithSubSections:
        phase = phase_name_dictionary()
        instruction = AnyInstructionNameDictionary()
        rest_paragraphs = []
        sub_sections = []
        rest_paragraphs.extend(normalize_and_parse(_SANDBOX_PRE_DIRECTORY_TREE.format(phase=phase)))
        sub_sections.append(directory_structure_list_section(sds.execution_directories))
        sub_sections.extend(sandbox_directories_info_sections(phase, instruction))
        return DescriptionWithSubSections(docs.text(_SANDBOX_SINGLE_LINE_DESCRIPTION),
                                          SectionContents(rest_paragraphs, sub_sections))

    def see_also(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(SETUP_PHASE_NAME.plain,
                                                   CHANGE_DIR_INSTRUCTION_NAME),
        ]


SANDBOX_CONCEPT = _Sandbox()

_SANDBOX_SINGLE_LINE_DESCRIPTION = """\
The temporary directory structure where a test case is executed."""

_SANDBOX_PRE_DIRECTORY_TREE = """\
Each test case uses its own sandbox.


The sandbox is created just before the {phase[setup]} phase is executed.
"""


def sandbox_directories_info_sections(phase_name_dictionary: dict,
                                      instruction: AnyInstructionNameDictionary) -> list:
    def section(directory_name: str, paragraph_items: list) -> Section:
        return docs.section('%s/' % directory_name,
                            paragraph_items)

    return [
        section(sds.SUB_DIRECTORY__ACT,
                _act_dir_description_paragraphs(instruction, phase_name_dictionary)),
        section(sds.SUB_DIRECTORY__RESULT,
                _result_dir_description_paragraphs(instruction, phase_name_dictionary)),
    ]


def _act_dir_description_paragraphs(instruction: AnyInstructionNameDictionary, phase: dict) -> list:
    ret_val = []
    ret_val.extend(normalize_and_parse(
        _ACT_DIR_DESCRIPTION.format(phase=phase,
                                    instruction=instruction,
                                    pwd=formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT_NAME.singular))))
    ret_val.extend(_act_dir_environment_variables(phase=phase))
    return ret_val


def _result_dir_description_paragraphs(instruction: AnyInstructionNameDictionary, phase: dict):
    ret_val = []
    ret_val.extend(normalize_and_parse(
        _RESULT_DIR_DESCRIPTION.format(phase=phase,
                                       instruction=instruction)))
    ret_val.append(docs.simple_header_only_list(sds.RESULT_FILE_ALL,
                                                lists.ListType.VARIABLE_LIST))
    ret_val.extend(_result_dir_environment_variables(phase))
    return ret_val


_ACT_DIR_DESCRIPTION = """\
This directory is the {pwd} when the {phase[setup]} phase begin.


If it is not changed, it will also be the {pwd} for the {phase[act]} phase (hence its name).


(Files and directories that {phase[setup]:syntax} creates
are installed into the {pwd}, if no instruction options are used to change this.)
"""
_RESULT_DIR_DESCRIPTION = """\
This directory is initially empty.

It is populated when the {phase[act]} phase is executed
with the following files (with obvious contents):
"""


def _result_dir_environment_variables(phase: dict) -> list:
    return docs.paras('{env_var}: The value of this environment variable is the absolute path of this directory '
                      '(after the {phase[act]} phase has been executed).'
                      .format(phase=phase,
                              env_var=ENV_VAR_RESULT))


def _act_dir_environment_variables(phase: dict) -> list:
    return docs.paras('{env_var}: The value of this environment variable is the absolute path of this directory.'
                      .format(phase=phase,
                              env_var=ENV_VAR_ACT))


def directory_structure_list_section(dir_with_sub_dir_list: list) -> Section:
    return docs.section('Directory structure',
                        [_directory_structure_list(dir_with_sub_dir_list)])


def _directory_structure_list(dir_with_sub_dir_list: list) -> ParagraphItem:
    items = []
    for dir_wsd in sorted(dir_with_sub_dir_list, key=lambda x: x.name):
        sub_dirs_items = []
        if dir_wsd.sub_dirs:
            sub_dirs_items = [_directory_structure_list(dir_wsd.sub_dirs)]
        items.append(lists.HeaderContentListItem(docs.text(dir_wsd.name + '/'), sub_dirs_items))
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST))
