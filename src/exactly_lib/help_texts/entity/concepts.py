from exactly_lib import program_info
from exactly_lib.help.utils.entity_documentation import command_line_names_as_singular_name
from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity_identifiers import CONCEPT_ENTITY_TYPE_IDENTIFIER
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME, phase_name_dictionary
from exactly_lib.util.name import Name, name_with_plural_s

CONCEPT_ENTITY_TYPE_NAMES = command_line_names_as_singular_name(CONCEPT_ENTITY_TYPE_IDENTIFIER,
                                                                name_with_plural_s('concept'))


def concept_cross_ref(concept_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(CONCEPT_ENTITY_TYPE_NAMES.identifier,
                                  CONCEPT_ENTITY_TYPE_NAMES.name.singular,
                                  concept_name)


def name_and_ref_target(name: Name,
                        single_line_description_str: str) -> SingularAndPluralNameAndCrossReferenceId:
    return SingularAndPluralNameAndCrossReferenceId(name,
                                                    single_line_description_str,
                                                    concept_cross_ref(name.singular))


def _format(s: str) -> str:
    return s.format(program_name=formatting.program_name(program_info.PROGRAM_NAME),
                    phase=phase_name_dictionary())


_CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION = """\
A value set in the {0} phase that determine how the remaining phases are executed."""

CONFIGURATION_PARAMETER_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('configuration parameter'),
    _CONFIGURATION_PARAMETER_SINGLE_LINE_DESCRIPTION.format(CONFIGURATION_PHASE_NAME)
)

TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('test case directory structure'),
    'Preexisting and temporary directories used during the execution of a test case.'
)

HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('home directory structure'),
    'Preexisting directories where source files are located.'
)

SANDBOX_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('sandbox directory structure'),
    'Temporary directories used during a single execution of a test case.'
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

SUITE_REPORTER_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('suite reporter'),
    'Reports the outcome of a test suite via stdout, stderr and exit code.'
)

TYPE_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('type'),
    'Type system for symbols and instruction arguments.'
)

SYMBOL_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('symbol'),
    'A named, constant, value.'
)

ACTOR_CONCEPT_INFO = name_and_ref_target(
    name_with_plural_s('actor'),
    _format('Interprets the contents of the {phase[act]} phase, and executes it.')
)
