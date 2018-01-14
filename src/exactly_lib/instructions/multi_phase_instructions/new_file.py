from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase_instructions.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForErrorMessageStringResultAsHardError
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import InstructionPartsParser
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.file_maker import FileMaker
from exactly_lib.instructions.utils.parse.parse_file_maker import CONTENTS_ASSIGNMENT_TOKEN, CONTENTS_ARGUMENT, \
    InstructionConfig, parse_file_contents, \
    FileContentsDocumentation, \
    _src_rel_opt_arg_conf_for_phase
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths, \
    InstructionSourceInfo
from exactly_lib.test_case_utils.parse.parse_file_ref import parse_file_ref_from_token_parser
from exactly_lib.test_case_utils.parse.rel_opts_configuration import argument_configuration_for_file_creation
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


def parts_parser(instruction_name: str,
                 phase_is_after_act: bool) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(EmbryoParser(instruction_name, phase_is_after_act),
                                       MainStepResultTranslatorForErrorMessageStringResultAsHardError())


RUN_PROGRAM_TOKEN = instruction_names.RUN_INSTRUCTION_NAME


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str,
                 phase_is_after_act: bool):
        super().__init__(name, {})
        self._src_rel_opt_arg_conf = _src_rel_opt_arg_conf_for_phase(phase_is_after_act)
        self._file_contents_doc = FileContentsDocumentation(phase_is_after_act, CONTENTS_ARGUMENT)

        self._tp = TextParser({
            'CONTENTS': CONTENTS_ARGUMENT,
        })

    def single_line_description(self) -> str:
        return 'Creates a file'

    def invokation_variants(self) -> list:
        arguments = path_syntax.mandatory_path_with_optional_relativity(
            _DST_PATH_ARGUMENT,
            REL_OPT_ARG_CONF.path_suffix_is_required)
        contents_arg = a.Single(a.Multiplicity.MANDATORY,
                                a.Named(CONTENTS_ARGUMENT))
        assignment_arg = a.Single(a.Multiplicity.MANDATORY,
                                  a.Constant(CONTENTS_ASSIGNMENT_TOKEN))
        return [
            invokation_variant_from_args(arguments,
                                         docs.paras('Creates an empty file.')),
            invokation_variant_from_args(arguments + [assignment_arg, contents_arg],
                                         self._tp.paras('Creates a file with contents given by {CONTENTS}.')),
        ]

    def syntax_element_descriptions(self) -> list:
        ret_val = [
            rel_path_doc.path_element(_DST_PATH_ARGUMENT.name,
                                      REL_OPT_ARG_CONF.options,
                                      docs.paras(the_path_of('a non-existing file.'))),
        ]
        ret_val += self._file_contents_doc.syntax_element_descriptions()

        return ret_val

    def see_also_targets(self) -> list:
        return [syntax_elements.PATH_SYNTAX_ELEMENT.cross_reference_target] + self._file_contents_doc.see_also_targets()


class TheInstructionEmbryo(embryo.InstructionEmbryo):
    def __init__(self,
                 path_to_create: FileRefResolver,
                 file_maker: FileMaker):
        self._path_to_create = path_to_create
        self._file_maker = file_maker

    @property
    def symbol_usages(self) -> list:
        return self._path_to_create.references + self._file_maker.symbol_references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._file_maker.validator

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices) -> str:
        path_to_create = self._path_to_create.resolve_value_of_any_dependency(
            environment.path_resolving_environment_pre_or_post_sds)
        return self._file_maker.make(environment, path_to_create)


class EmbryoParser(embryo.InstructionEmbryoParser):
    def __init__(self,
                 instruction_name: str,
                 phase_is_after_act: bool):
        self._phase_is_after_act = phase_is_after_act
        self._instruction_name = instruction_name

    def parse(self, source: ParseSource) -> embryo.InstructionEmbryo:
        first_line_number = source.current_line_number
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            assert isinstance(parser, TokenParser)  # Type info for IDE

            path_to_create = parse_file_ref_from_token_parser(REL_OPT_ARG_CONF, parser)
            instruction_config = InstructionConfig(
                InstructionSourceInfo(first_line_number,
                                      self._instruction_name),
                _src_rel_opt_arg_conf_for_phase(self._phase_is_after_act)
            )

            file_maker = parse_file_contents(instruction_config, parser)

            return TheInstructionEmbryo(path_to_create, file_maker)


_DST_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

REL_OPT_ARG_CONF = argument_configuration_for_file_creation(_DST_PATH_ARGUMENT.name)
