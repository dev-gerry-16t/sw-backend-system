import datetime
import pytz
from dateutil.relativedelta import relativedelta

class FormatDate:
    def __init__(self):
        self.date_utc = datetime.datetime.now(pytz.utc)

    def format_iso(self):
        format_iso = self.date_utc.strftime('%Y-%m-%dT%H:%M:%S%z')
        return format_iso

    def timezone_cdmx(self):
        zone_cdmx = pytz.timezone('America/Mexico_City')
        date_cdmx = self.date_utc.astimezone(zone_cdmx)
        format_iso_cdmx = date_cdmx.strftime('%Y-%m-%dT%H:%M:%S%z')
        return format_iso_cdmx
    
    def unix_timestamp_to_iso(self, unix_timestamp):
        date = datetime.datetime.fromtimestamp(unix_timestamp, tz=pytz.utc)
        offset = datetime.timedelta(hours=-6)
        dt_with_offset = date.astimezone(pytz.timezone('America/Mexico_City')) + offset
        format_iso = dt_with_offset.strftime('%Y-%m-%dT%H:%M:%S%z')
        return format_iso
    
    def add_single_month(self, date = None):
        if date is None:
            date = self.timezone_cdmx()

        initial_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        final_date = initial_date + relativedelta(months=1)

        return final_date.strftime('%Y-%m-%dT%H:%M:%S%z')
    
    def date_format_now(self):
        date_now = datetime.datetime.now()
        date_format = date_now.strftime('%d/%B/%Y')
        return date_format
    
    def diff_dates_since_now(self, date):
        final_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        initial_date = datetime.datetime.now(final_date.tzinfo)

        difference = final_date - initial_date
        return difference.days


