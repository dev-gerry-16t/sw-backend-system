from datetime import datetime 
import pytz
from dateutil.relativedelta import relativedelta

class FormatDate:
    def __init__(self):
        self.date_utc = datetime.now(pytz.utc)

    def format_iso(self):
        format_iso = self.date_utc.strftime('%Y-%m-%dT%H:%M:%S%z')
        return format_iso

    def timezone_cdmx(self):
        zone_cdmx = pytz.timezone('America/Mexico_City')
        date_cdmx = self.date_utc.astimezone(zone_cdmx)
        format_iso_cdmx = date_cdmx.strftime('%Y-%m-%dT%H:%M:%S%z')
        return format_iso_cdmx
    
    def add_single_month(self, date = None):
        if date is None:
            date = self.timezone_cdmx()

        initial_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        final_date = initial_date + relativedelta(months=1)

        return final_date.strftime('%Y-%m-%dT%H:%M:%S%z')
    
    def diff_dates_since_now(self, date):
        final_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        initial_date = datetime.now(final_date.tzinfo)

        difference = final_date - initial_date
        return difference.days


