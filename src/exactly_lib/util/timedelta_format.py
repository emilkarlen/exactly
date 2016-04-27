import datetime


def elapsed_time_value_and_unit(td: datetime.timedelta) -> (str, str):
    unit = 'days'
    s = str(td)
    if s[:2] == '0:':
        s = s[2:]
        unit = 'min'
        if s[:3] == '00:':
            s = s[3:]
            unit = 's'
            if s[0] == '0':
                s = s[1:]
    return (s, unit)
