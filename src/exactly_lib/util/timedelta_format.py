import datetime


def elapsed_time_value_and_unit(td: datetime.timedelta) -> (str, str):
    s = '%f' % td.total_seconds()
    return (s, 's')
