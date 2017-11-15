from exactly_lib.help.entities.suite_reporters.objects import junit
from exactly_lib.help.entities.suite_reporters.objects.progress_reporter import DOCUMENTATION

ALL_SUITE_REPORTERS = [
    DOCUMENTATION,
    junit.JunitSuiteReporterDocumentation(),
]
