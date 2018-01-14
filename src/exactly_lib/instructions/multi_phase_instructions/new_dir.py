from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.cross_ref import name_and_cross_ref
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase_instructions.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForErrorMessageStringResultAsHardError
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.parse.token_stream_parse import TokenParserExtra
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case_utils.parse.rel_opts_configuration import argument_configuration_for_file_creation
from exactly_lib.util.textformat.structure import structures as docs


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        super().__init__(name, {}, is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._format('Creates a directory')

    def _main_description_rest_body(self) -> list:
        text = """\
            Creates parent directories if needed.


            Does nothing if the given directory already exists.
            """
        return self._paragraphs(text)

    def invokation_variants(self) -> list:
        arguments = path_syntax.mandatory_path_with_optional_relativity(
            _PATH_ARGUMENT,
            RELATIVITY_VARIANTS.path_suffix_is_required)
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              []),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            rel_path_doc.path_element(_PATH_ARGUMENT.name,
                                      RELATIVITY_VARIANTS.options,
                                      docs.paras(the_path_of('a non-existing file.')))
        ]

    def see_also_targets(self) -> list:
        name_and_cross_refs = [syntax_elements.PATH_SYNTAX_ELEMENT]
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)


class TheInstructionEmbryo(embryo.InstructionEmbryo):
    def __init__(self, dir_path_resolver: FileRefResolver):
        self.dir_path_resolver = dir_path_resolver

    @property
    def symbol_usages(self) -> list:
        return self.dir_path_resolver.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices):
        return self.custom_main(environment.path_resolving_environment)

    def custom_main(self, environment: PathResolvingEnvironmentPostSds) -> str:
        """
        :return: None iff success. Otherwise an error message.
        """
        dir_path = self.dir_path_resolver.resolve(environment.symbols).value_post_sds(environment.sds)
        try:
            if dir_path.is_dir():
                return None
        except NotADirectoryError:
            return 'Part of PATH exists, but is not a directory: %s' % str(dir_path)
        try:
            dir_path.mkdir(parents=True)
        except FileExistsError:
            return 'PATH exists, but is not a directory: {}'.format(dir_path)
        except NotADirectoryError:
            return 'Clash with existing file: {}'.format(dir_path)
        return None


class EmbryoParser(embryo.InstructionEmbryoParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> TheInstructionEmbryo:
        tokens = TokenParserExtra(TokenStream(rest_of_line))

        target_file_ref = tokens.consume_file_ref(RELATIVITY_VARIANTS)
        tokens.report_superfluous_arguments_if_not_at_eol()
        return TheInstructionEmbryo(target_file_ref)


PARTS_PARSER = PartsParserFromEmbryoParser(EmbryoParser(),
                                           MainStepResultTranslatorForErrorMessageStringResultAsHardError())

_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

RELATIVITY_VARIANTS = argument_configuration_for_file_creation(_PATH_ARGUMENT.name)
