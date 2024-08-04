

import datetime
from enum import Enum
import time
from typing import Dict, List

from helpers.supabase_db import SupabaseDB

class Tables(Enum):
    NEWS = 'news'

    def __str__(self):
        return self.value


class HeadlineManager:

    def __init__(self, db: SupabaseDB) -> None:
        """Initialize the HeadlineManager with the given API and database."""
        self.db = db

    
    def save(self, headline: Dict) -> List:
        """Save the given headline to the database."""
        return self.db.create_or_update(Tables.NEWS, headline)
    
    def exists(self, url: int) -> bool:
        """Check if the given headline exists."""
        return len(self.db.read(Tables.NEWS, {"url": url})) > 0
    
    def validate(self, headline_id: int, validated: bool) -> None:
        """Validate the given headline."""
        useful = True
        
        if validated is None:   # None for the headline is misogyny but no useful
            validated = True
            useful = False

        self.db.update(Tables.NEWS, {"id": headline_id}, {"validated": validated, "useful": useful})