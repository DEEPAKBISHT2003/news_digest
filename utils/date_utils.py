from datetime import datetime

def get_current_date_context():
    now = datetime.now()

    return {
        "day": now.strftime("%d"),
        "month": now.strftime("%B"),
        "year": now.strftime("%Y"),
        "full_date": now.strftime("%d %B %Y")
    }