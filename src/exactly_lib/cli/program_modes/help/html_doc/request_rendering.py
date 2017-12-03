from exactly_lib.cli.program_modes.help.request_handling.request_handler import RequestHandler
from exactly_lib.help.contents_structure.application import ApplicationHelp
from exactly_lib.help.html_doc import main as html_doc
from exactly_lib.util.std import StdOutputFiles


class HtmlGenerationRequestHandler(RequestHandler):
    def __init__(self,
                 application_help: ApplicationHelp):
        self.application_help = application_help

    def handle(self,
               output: StdOutputFiles):
        html_doc.generate_and_output(output.out, self.application_help)
