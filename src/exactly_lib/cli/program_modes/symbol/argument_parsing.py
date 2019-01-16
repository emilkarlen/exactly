from typing import List, Dict

from exactly_lib.cli.program_modes.symbol import request
from exactly_lib.cli.program_modes.symbol.request import SymbolInspectionRequest
from exactly_lib.cli.program_modes.test_case import argument_parsing as case_arg_parsing
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.symbol import symbol_syntax
from exactly_lib.util.argument_parsing_utils import ArgumentParsingError


def parse(default: TestCaseHandlingSetup,
          default_sandbox_root_dir_name_resolver: SandboxRootDirNameResolver,
          argv: List[str],
          commands: Dict[str, str]) -> SymbolInspectionRequest:
    case_settings, remaining_args = case_arg_parsing.parse_known_args(default,
                                                                      default_sandbox_root_dir_name_resolver,
                                                                      argv,
                                                                      commands)

    request_variant = _resolve_request_variant(remaining_args)

    return SymbolInspectionRequest(case_settings,
                                   request_variant)


def _resolve_request_variant(remaining_args: List[str]) -> request.RequestVariant:
    num_remaining_args = len(remaining_args)
    if num_remaining_args == 0:
        return request.RequestVariantList()
    elif num_remaining_args == 1:
        symbol_name_arg = remaining_args[0]
        if not symbol_syntax.is_symbol_name(symbol_name_arg):
            raise ArgumentParsingError('Not a valid symbol name: ' + symbol_name_arg)
        return request.RequestVariantIndividual(symbol_name_arg)
    else:
        superfluous_args_str = ' '.join(remaining_args[1:])
        raise ArgumentParsingError('Superfluous arguments: ' + superfluous_args_str)
