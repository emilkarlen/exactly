from exactly_lib.help.suite_reporters.suite_reporter import junit
from exactly_lib.help.suite_reporters.suite_reporter.progress_reporter import DOCUMENTATION

ALL_SUITE_REPORTERS = [
    DOCUMENTATION,
    junit.JunitSuiteReporterDocumentation(),
]
