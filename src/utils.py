def seconds_to_timestamp(seconds: float) -> str:
    total_milliseconds = int(seconds * 1000)

    hours = total_milliseconds // 3_600_000
    minutes = (total_milliseconds % 3_600_000) // 60_000
    secs = (total_milliseconds % 60_000) // 1000
    millis = total_milliseconds % 1000

    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def seconds_to_readable_time(seconds: float) -> str:
    total_seconds = int(seconds)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    return f"{hours:02}:{minutes:02}:{secs:02}"