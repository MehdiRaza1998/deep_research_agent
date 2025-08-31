from agents import function_tool
from datetime import datetime

@function_tool
def get_today_date():
    """
    Get the current date and time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
