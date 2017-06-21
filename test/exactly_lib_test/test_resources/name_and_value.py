class NameAndValue(tuple):
    def __new__(cls,
                name, value):
        return tuple.__new__(cls, (name, value))

    @property
    def name(self):
        return self[0]

    @property
    def value(self):
        return self[1]
