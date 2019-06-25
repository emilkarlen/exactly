from typing import List, Dict

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.cli.definitions.program_modes.symbol import command_line_options
from exactly_lib.cli.program_modes.symbol import request
from exactly_lib.cli.program_modes.symbol.request import SymbolInspectionRequest
from exactly_lib.cli.program_modes.test_case import argument_parsing as case_arg_parsing
from exactly_lib.cli.program_modes.test_suite import argument_parsing as suite_arg_parsing
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.symbol import symbol_syntax
from exactly_lib.util.argument_parsing_utils import ArgumentParsingError


def parse(default: TestCaseHandlingSetup,
          default_sandbox_root_dir_name_resolver: SandboxRootDirNameResolver,
          argv: List[str],
          commands: Dict[str, str]) -> SymbolInspectionRequest:
    if argv and argv[0] == common_cli_options.SUITE_COMMAND:
        suite_settings, remaining_args = suite_arg_parsing.parse_known_args(default, argv[1:])
        request_variant = _resolve_request_variant(remaining_args)

        return SymbolInspectionRequest.new_for_suite(suite_settings,
                                                     request_variant)
    else:
        case_settings, remaining_args = case_arg_parsing.parse_known_args(default,
                                                                          default_sandbox_root_dir_name_resolver,
                                                                          argv,
                                                                          commands)
        request_variant = _resolve_request_variant(remaining_args)

        return SymbolInspectionRequest.new_for_case(case_settings,
                                                    request_variant)


def _resolve_request_variant(remaining_args: List[str]) -> request.RequestVariant:
    if len(remaining_args) == 0:
        return request.RequestVariantList()

    symbol_name_arg = remaining_args[0]
    del remaining_args[0]

    if not symbol_syntax.is_symbol_name(symbol_name_arg):
        raise ArgumentParsingError('Not a valid symbol name: ' + symbol_name_arg)

    if len(remaining_args) == 0:
        return request.RequestVariantIndividual(symbol_name_arg, list_references=False)

    if remaining_args[0] == command_line_options.OPTION_FOR_SYMBOL_REFERENCES:
        del remaining_args[0]

    if len(remaining_args) == 0:
        return request.RequestVariantIndividual(symbol_name_arg, list_references=True)
    else:
        superfluous_args_str = ' '.join(remaining_args)
        raise ArgumentParsingError('Invalid arguments: ' + superfluous_args_str)
