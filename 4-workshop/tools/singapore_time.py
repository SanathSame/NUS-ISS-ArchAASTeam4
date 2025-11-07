from datetime import datetime
import pytz

def singapore_time() -> str:
    """Get current time in Singapore."""
    sg_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(sg_tz)
    return now.strftime("%I:%M %p, %d %B %Y")