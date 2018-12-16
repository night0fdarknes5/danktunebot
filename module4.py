from datetime import datetime, timezone

unix_timestamp = 1543233306.001300

utc_time = datetime.fromtimestamp(unix_timestamp, timezone.utc)
local_time = utc_time.astimezone()
print(local_time.strftime("%H:%M %d/%m/%Y"))
