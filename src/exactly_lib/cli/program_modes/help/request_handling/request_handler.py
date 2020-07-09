from exactly_lib.util.file_utils.std import StdOutputFiles


class RequestHandler:
    def handle(self,
               output: StdOutputFiles):
        raise NotImplementedError()
