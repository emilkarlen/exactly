from exactly_lib import program_info
from exactly_lib.common.help.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.default.program_modes.test_case.default_instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.execution import environment_variables
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help.concepts.names_and_cross_references import SANDBOX_CONCEPT_INFO
from exactly_lib.help.concepts.some_concept_names import CURRENT_WORKING_DIRECTORY_CONCEPT_NAME
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.formatting import AnyInstructionNameDictionary, InstructionName
from exactly_lib.help.utils.phase_names import phase_name_dictionary, SETUP_PHASE_NAME
from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.test_case import sandbox_directory_structure as sds
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents, Section


class _Sandbox(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(SANDBOX_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        phase = phase_name_dictionary()
        instruction = AnyInstructionNameDictionary()
        rest_paragraphs = []
        sub_sections = []
        rest_paragraphs.extend(normalize_and_parse(_SANDBOX_PRE_DIRECTORY_TREE.format(phase=phase)))
        sub_sections.append(directory_structure_list_section(sds.execution_directories))
        sub_sections.extend(sandbox_directories_info_sections(phase, instruction))
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs, sub_sections))

    def _see_also_cross_refs(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(SETUP_PHASE_NAME.plain,
                                                   CHANGE_DIR_INSTRUCTION_NAME),
        ]


SANDBOX_CONCEPT = _Sandbox()

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
        section(sds.SUB_DIRECTORY__TMP + '/' + sds.SUB_DIRECTORY__TMP_USER,
                _tmp_user_dir_description_paragraphs()),
        docs.section('Other directories',
                     _other_directories_than_those_listed())
    ]


def _act_dir_description_paragraphs(instruction: AnyInstructionNameDictionary, phase: dict) -> list:
    ret_val = []
    ret_val.extend(normalize_and_parse(
        _ACT_DIR_DESCRIPTION.format(phase=phase,
                                    instruction=instruction,
                                    cwd=formatting.concept(CURRENT_WORKING_DIRECTORY_CONCEPT_NAME.singular),
                                    cd_instruction=InstructionName(CHANGE_DIR_INSTRUCTION_NAME))))
    ret_val.extend(_dir_env_variables_and_rel_options(env_var_name=environment_variables.ENV_VAR_ACT,
                                                      rel_option=relative_path_options.REL_ACT_OPTION))
    return ret_val


def _result_dir_description_paragraphs(instruction: AnyInstructionNameDictionary, phase: dict):
    ret_val = []
    ret_val.extend(normalize_and_parse(
        _RESULT_DIR_DESCRIPTION.format(phase=phase,
                                       instruction=instruction)))
    ret_val.append(docs.simple_header_only_list(sds.RESULT_FILE_ALL,
                                                lists.ListType.ITEMIZED_LIST))
    ret_val.extend(_result_dir_env_variable_and_rel_option(phase))
    return ret_val


def _tmp_user_dir_description_paragraphs():
    ret_val = []
    ret_val.extend(normalize_and_parse(
        _USR_TMP_DIR_DESCRIPTION.format(program_name=formatting.program_name(program_info.PROGRAM_NAME))))
    ret_val.extend(_dir_env_variables_and_rel_options(env_var_name=environment_variables.ENV_VAR_TMP,
                                                      rel_option=relative_path_options.REL_TMP_OPTION))
    return ret_val


_ACT_DIR_DESCRIPTION = """\
This directory is the {cwd} when the {phase[setup]} phase begin.


If it is not changed by the {cd_instruction} instruction,
it will also be the {cwd} for the {phase[act]} phase.


(Files and directories that {phase[setup]:syntax} creates
are installed into the {cwd}, if no instruction options are used to change this.)
"""

_RESULT_DIR_DESCRIPTION = """\
This directory is initially empty.

It is populated when the {phase[act]} phase is executed
with the following files (with obvious contents):
"""

_USR_TMP_DIR_DESCRIPTION = """\
A directory that the writer of the test case can store arbitrary files.

{program_name} does not touch contents of this directory.
"""


def _result_dir_env_variable_and_rel_option(phase: dict) -> list:
    return [_dir_info_items_table(environment_variables.ENV_VAR_RESULT,
                                  relative_path_options.REL_RESULT_OPTION,
                                  _RESULT_DIR_ENV_VARIABLE.format(phase=phase))
            ]


_RESULT_DIR_ENV_VARIABLE = """\
The value of this environment variable
is the absolute path of this directory
(after the {phase[act]} phase has been executed)."""


def _dir_env_variables_and_rel_options(env_var_name: str,
                                       rel_option: str) -> list:
    return [_dir_info_items_table(env_var_name,
                                  rel_option,
                                  'The value of this environment variable is the absolute path of this directory.')
            ]


def _dir_info_items_table(env_var_name: str,
                          rel_option: str,
                          env_var_description: str) -> ParagraphItem:
    return docs.first_column_is_header_table([
        [
            docs.cell(docs.paras(env_var_name)),
            docs.cell(docs.paras(env_var_description)),
        ],
        [
            docs.cell(docs.paras(rel_option)),
            docs.cell(docs.paras('This option (accepted by many instructions) refers to this directory.')),
        ],
    ])


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
                                   lists.Format(lists.ListType.ITEMIZED_LIST))


def _other_directories_than_those_listed() -> list:
    return docs.normalize_and_parse(_OTHER_DIRECTORIES_THAN_THOSE_LISTED.format(
        program_name=formatting.program_name(program_info.PROGRAM_NAME)))


_OTHER_DIRECTORIES_THAN_THOSE_LISTED = """\
The directories not mentioned above are reserved for {program_name},
and should not be touched.
"""
