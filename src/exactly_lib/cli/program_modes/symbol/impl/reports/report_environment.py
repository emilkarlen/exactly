from exactly_lib.cli.program_modes.symbol.impl.completion_reporter import CompletionReporter
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import DefinitionsResolver
from exactly_lib.util.std import StdOutputFiles


class Environment:
    def __init__(self,
                 output: StdOutputFiles,
                 completion_reporter: CompletionReporter,
                 definitions_resolver: DefinitionsResolver):
        self.output = output
        self.completion_reporter = completion_reporter
        self.definitions_resolver = definitions_resolver
