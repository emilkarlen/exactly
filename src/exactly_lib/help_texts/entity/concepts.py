from exactly_lib import program_info
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId, \
    EntityTypeNames
from exactly_lib.help_texts.entity import all_entity_types
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME, PHASE_NAME_DICTIONARY
from exactly_lib.util.name import Name, name_with_plural_s


def concept_cross_ref(concept_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(all_entity_types.CONCEPT_ENTITY_TYPE_NAMES,
                                  concept_name)


def name_and_ref_target(name: Name,
                        single_line_description_str: str) -> SingularAndPluralNameAndCrossReferenceId:
    return SingularAndPluralNameAndCrossReferenceId(name,
                                                    single_line_description_str,
                                                    concept_cross_ref(name.singular))


def name_and_ref_target_for_entity_type(names: EntityTypeNames,
                                        single_line_description_str: str) -> SingularAndPluralNameAndCrossReferenceId:
    return name_and_ref_target(names.name, single_line_description_str)


def _format(s: str) -> str:
    return s.format(program_name=formatting.program_name(program_info.PROGRAM_NAME),
                    phase=PHASE_NAME_DICTIONARY)


_CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION = """\
A value set in the {0} phase that determine how the remaining phases are executed."""

CONFIGURATION_PARAMETER_CONCEPT_INFO = name_and_ref_target_for_entity_type(
    all_entity_types.CONF_PARAM_ENTITY_TYPE_NAMES,
    _CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION.format(CONFIGURATION_PHASE_NAME)
)

TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('test case directory structure'),
    'Predefined and temporary directories used during the execution of a test case.'
)

HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('home directory structure'),
    'Predefined directories and files accessed by a test case.'
)

SANDBOX_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('sandbox directory structure'),
    _format('Temporary directories used during a single execution of a test case, '
            'one of which is the current directory when {phase[setup]:syntax} begins'),
)

CURRENT_WORKING_DIRECTORY_CONCEPT_INFO = name_and_ref_target(
    Name('current directory', 'current directories'),
    'The current directory of the environment in which an instruction is executed.'
)

ENVIRONMENT_VARIABLE_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('environment variable'),
    _format('Environment variables set by {program_name}.')
)

PREPROCESSOR_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('preprocessor'),
    'A program that transforms a test case file as the first step in the processing of it.'
)

SHELL_SYNTAX_CONCEPT_INFO = name_and_ref_target(
    Name('shell syntax', "shell syntaxes"),
    'Quoting of strings in command lines.'
)

SUITE_REPORTER_CONCEPT_INFO = name_and_ref_target_for_entity_type(
    all_entity_types.SUITE_REPORTER_ENTITY_TYPE_NAMES,
    'Reports the outcome of a test suite via stdout, stderr and exit code.'
)

TYPE_CONCEPT_INFO = name_and_ref_target_for_entity_type(
    all_entity_types.TYPE_ENTITY_TYPE_NAMES,
    'Type system for symbols and instruction arguments.'
)

SYMBOL_CONCEPT_INFO = name_and_ref_target(
    all_entity_types.SYMBOL_CONCEPT_NAME,
    'A named, constant, value.'
)

ACTOR_CONCEPT_INFO = name_and_ref_target_for_entity_type(
    all_entity_types.ACTOR_ENTITY_TYPE_NAMES,
    _format('Interprets the contents of the {phase[act]} phase, and executes it.')
)
