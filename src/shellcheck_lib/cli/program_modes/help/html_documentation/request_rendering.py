from shellcheck_lib.cli.program_modes.help.request_handling.request_handler import RequestHandler
from shellcheck_lib.help.contents_structure import ApplicationHelp
from shellcheck_lib.help.html_doc.main import HtmlDocGenerator
from shellcheck_lib.util.std import StdOutputFiles


class HtmlGenerationRequestHandler(RequestHandler):
    def __init__(self,
                 application_help: ApplicationHelp):
        self.application_help = application_help

    def handle(self,
               output: StdOutputFiles):
        generator = HtmlDocGenerator(output, self.application_help)
        generator.apply()
