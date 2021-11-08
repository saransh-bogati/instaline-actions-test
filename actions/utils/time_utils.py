from datetime import tzinfo, time, datetime, date, timedelta

WEEK_DAY = (
    "MON",
    "TUE",
    "WED",
    "THU",
    "FRI",
    "SAT",
    "SUN"
)


def get_date_from_weekday(day_str: str = None):
    current_date = datetime.now()
    first_day = current_date - timedelta(days=current_date.weekday())


def parse_period(time_string: str, src_tz: tzinfo, day_str: str = None, future_date: bool = False):
    if time_string == "24:00:00":
        time_obj = time.fromisoformat("00:00:00")
        time_today = datetime.combine(date.today() + timedelta(days=1), time_obj, tzinfo=src_tz)
    else:
        time_obj = time.fromisoformat(time_string)
        time_today = datetime.combine(date.today(), time_obj, tzinfo=src_tz)

    if day_str is None:
        return time_today

    # Normalize day
    today = time_today.weekday()
    weekday = WEEK_DAY.index(day_str)
    if weekday == today:
        return time_today

    first_day_of_week = time_today - timedelta(days=time_today.weekday())
    if future_date and weekday >= today:
        normalized_weekday = first_day_of_week + timedelta(days=weekday)
    else:
        normalized_weekday = first_day_of_week + timedelta(days=weekday + 7)

    return normalized_weekday
