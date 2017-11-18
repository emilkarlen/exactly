from exactly_lib import program_info
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.names.formatting import AnyInstructionNameDictionary, InstructionName
from exactly_lib.help_texts.test_case.instructions.instruction_names import CHANGE_DIR_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import SETUP_PHASE_NAME, PHASE_NAME_DICTIONARY
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds, environment_variables
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents, Section
from exactly_lib.util.textformat.textformat_parser import TextParser


class _SandboxConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.SANDBOX_CONCEPT_INFO)

        self._tp = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'phase': PHASE_NAME_DICTIONARY,
            'instruction': AnyInstructionNameDictionary(),
            'cwd': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'cd_instruction': InstructionName(CHANGE_DIR_INSTRUCTION_NAME),
        })

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = []
        sub_sections = []
        rest_paragraphs += self._tp.fnap(_SANDBOX_PRE_DIRECTORY_TREE)
        sub_sections.append(directory_structure_list_section(sds.execution_directories))
        sub_sections += self._sandbox_directories_info_sections()
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs, sub_sections))

    def see_also_targets(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(SETUP_PHASE_NAME.plain,
                                                   CHANGE_DIR_INSTRUCTION_NAME),
            concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.cross_reference_target,
        ]

    def _sandbox_directories_info_sections(self) -> list:
        def section(directory_name: str, paragraph_items: list) -> Section:
            return docs.section('%s/' % directory_name,
                                paragraph_items)

        return [
            section(sds.SUB_DIRECTORY__ACT,
                    self._act_dir_description_paragraphs()),
            section(sds.SUB_DIRECTORY__RESULT,
                    self._result_dir_description_paragraphs()),
            section(sds.PATH__TMP_USER,
                    self._tmp_user_dir_description_paragraphs()),
            docs.section('Other directories',
                         self._other_directories_than_those_listed())
        ]

    def _act_dir_description_paragraphs(self) -> list:
        ret_val = []
        ret_val.extend(self._tp.fnap(_ACT_DIR_DESCRIPTION))
        ret_val.extend(_dir_env_variables_and_rel_options(env_var_name=environment_variables.ENV_VAR_ACT,
                                                          rel_option=file_ref_texts.REL_ACT_OPTION))
        return ret_val

    def _result_dir_description_paragraphs(self) -> list:
        ret_val = []
        ret_val += self._tp.fnap(_RESULT_DIR_DESCRIPTION)
        ret_val.append(docs.simple_header_only_list(sds.RESULT_FILE_ALL,
                                                    lists.ListType.ITEMIZED_LIST))
        ret_val += self._result_dir_env_variable_and_rel_option()
        return ret_val

    def _tmp_user_dir_description_paragraphs(self) -> list:
        ret_val = []
        ret_val += self._tp.fnap(_USR_TMP_DIR_DESCRIPTION)
        ret_val += _dir_env_variables_and_rel_options(env_var_name=environment_variables.ENV_VAR_TMP,
                                                      rel_option=file_ref_texts.REL_TMP_OPTION)
        return ret_val

    def _result_dir_env_variable_and_rel_option(self) -> list:
        return [_dir_info_items_table(environment_variables.ENV_VAR_RESULT,
                                      file_ref_texts.REL_RESULT_OPTION,
                                      self._tp.format(_RESULT_DIR_ENV_VARIABLE))
                ]

    def _other_directories_than_those_listed(self) -> list:
        return self._tp.fnap(_OTHER_DIRECTORIES_THAN_THOSE_LISTED)


SANDBOX_CONCEPT = _SandboxConcept()

_SANDBOX_PRE_DIRECTORY_TREE = """\
Each test case uses its own sandbox.


The sandbox is created just before the {phase[setup]} phase is executed,
and deleted after the test case has finished.
"""

_ACT_DIR_DESCRIPTION = """\
This directory is the {cwd} when the {phase[setup]} phase begin.


It will also be the {cwd} for the {phase[act]} phase, and following phases,
unless it is changed by the {cd_instruction} instruction.


(Files and directories that {phase[setup]:syntax} creates
are installed into the {cwd}, if no instruction options are used to change this.)
"""

_RESULT_DIR_DESCRIPTION = """\
This directory is initially empty.

It is populated when the {phase[act]} phase is executed
with the following files (with obvious contents):
"""

_USR_TMP_DIR_DESCRIPTION = """\
A directory that {program_name} does not touch.

The test case can use it as a place where it is safe to put temporary files without
the risk of clashes with files from other program.
"""

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


_OTHER_DIRECTORIES_THAN_THOSE_LISTED = """\
The directories not mentioned above are reserved for {program_name},
and should not be touched.
"""
