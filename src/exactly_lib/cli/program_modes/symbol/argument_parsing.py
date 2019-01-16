from typing import List, Dict

from exactly_lib.cli.program_modes.symbol.symbol_inspection import SymbolInspectionRequest
from exactly_lib.cli.program_modes.test_case import argument_parsing as case_arg_parsing
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup


def parse(default: TestCaseHandlingSetup,
          default_sandbox_root_dir_name_resolver: SandboxRootDirNameResolver,
          argv: List[str],
          commands: Dict[str, str]) -> SymbolInspectionRequest:
    case_settings = case_arg_parsing.parse(default,
                                           default_sandbox_root_dir_name_resolver,
                                           argv,
                                           commands)

    return SymbolInspectionRequest(case_settings)
