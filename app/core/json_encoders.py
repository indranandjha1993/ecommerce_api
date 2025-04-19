import json
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Any


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling UUID, datetime, date, and Decimal objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)