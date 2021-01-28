from typing import Optional, Sequence, TextIO

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls import file_creation
from exactly_lib.impls.instructions.multi_phase.new_file import defs
from exactly_lib.impls.instructions.utils import logic_type_resolving_helper
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib.impls.types.string_source import parse as parse_string_source
from exactly_lib.impls.types.string_source import sdvs as string_source_sdv
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_prims.described_path import DescribedPath
from exactly_lib.util.symbol_table import SymbolTable


class FileMaker:
    def __init__(self, string_source: StringSourceSdv):
        self._string_source = string_source

    @property
    def symbol_references(self) -> Sequence[SymbolReference]:
        return self._string_source.references

    @property
    def validator(self) -> SdvValidator:
        def get_ddv_validator(symbols: SymbolTable) -> DdvValidator:
            return self._string_source.resolve(symbols).validator

        return sdv_validation.SingleStepSdvValidator(
            sdv_validation.ValidationStep.PRE_SDS,
            sdv_validation.SdvValidatorFromDdvValidator(get_ddv_validator),
        )

    def make(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             dst_file: DescribedPath,
             ) -> Optional[TextRenderer]:
        try:
            self._validate_post_sds(environment)
            return self._create_file(environment, os_services, dst_file)
        except HardErrorException as ex:
            return ex.error

    def _create_file(self,
                     environment: InstructionEnvironmentForPostSdsStep,
                     os_services: OsServices,
                     dst_file: DescribedPath,
                     ) -> Optional[TextRenderer]:
        resoling_helper = logic_type_resolving_helper.resolving_helper_for_instruction_env(os_services, environment)
        string_source = resoling_helper.resolve_full(self._string_source)

        def write_sting_to_file(f: TextIO):
            string_source.contents().write_to(f)

        return file_creation.create_file__dp(dst_file, write_sting_to_file)

    def _validate_post_sds(self, environment: InstructionEnvironmentForPostSdsStep):
        validator = self._string_source.resolve(environment.symbols).validator
        mb_err_msg = validator.validate_post_sds_if_applicable(environment.tcds)
        if mb_err_msg:
            raise HardErrorException(mb_err_msg)


class FileMakerParser(ParserFromTokens):
    def __init__(self, src_rel_opt_conf: RelOptionsConfiguration):
        self._string_source_parser = parse_string_source.string_source_parser(src_rel_opt_conf)

    def parse(self, parser: TokenParser) -> FileMaker:
        contents = self._parse_string_source(parser)
        return FileMaker(contents)

    def _parse_string_source(self, token_parser: TokenParser) -> StringSourceSdv:
        """
        Parses a file contents specification of the form: [= FILE-MAKER]

        :raises SingleInstructionInvalidArgumentException: Invalid arguments
        """
        if token_parser.is_at_eol:
            return string_source_sdv.ConstantStringStringSourceSdv(string_sdvs.str_constant(''))
        else:
            token_parser.consume_mandatory_constant_unquoted_string(defs.CONTENTS_ASSIGNMENT_TOKEN, True)
            return self._string_source_parser.parse_from_token_parser(token_parser)
