class MainProgramHelp(tuple):
    def __new__(cls):
        return tuple.__new__(cls, ())
