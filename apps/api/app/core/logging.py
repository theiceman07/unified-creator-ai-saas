import json
import logging
from datetime import datetime


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, "run_id"):
            log_data["run_id"] = record.run_id
        if hasattr(record, "creator_hash"):
            log_data["creator_hash"] = record.creator_hash
            
        return json.dumps(log_data)

def setup_logging():
    logger = logging.getLogger("creatoros")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

logger = setup_logging()
