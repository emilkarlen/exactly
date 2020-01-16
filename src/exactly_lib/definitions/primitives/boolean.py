FALSE = 'false'
TRUE = 'true'

BOOLEANS = {
    False: FALSE,
    True: TRUE,
}

BOOLEANS_STRINGS = {
    item[1]: item[0]
    for item in BOOLEANS.items()
}

CONSTANT_MATCHER = 'constant'
