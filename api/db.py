import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from api.config import (
    MONGODB_URI,
    MONGODB_DB_NAME,
    MONGODB_COLLECTION_NAME,
    MONGODB_TIMEOUT_MS,
    FALLBACK_HISTORY_PATH,
)

logger = logging.getLogger("api.db")

class DatabaseManager:
    def __init__(self):
        self.uri = MONGODB_URI
        self.db_name = MONGODB_DB_NAME
        self.collection_name = MONGODB_COLLECTION_NAME
        self.fallback_file = Path(FALLBACK_HISTORY_PATH)
        self.fallback_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.fallback_file.exists():
            self._write_fallback([])
            
        self._client: Optional[MongoClient] = None
        self._is_connected = False
        self._init_client()

    def _init_client(self):
        try:
            self._client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=MONGODB_TIMEOUT_MS,
                connectTimeoutMS=MONGODB_TIMEOUT_MS,
            )
            # Quick ping to test connectivity
            self._client.admin.command("ping")
            self._is_connected = True
            logger.info("Successfully connected to MongoDB at %s", self.uri)
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            self._is_connected = False
            logger.warning("MongoDB unavailable (%s). Activating local fallback storage.", e)

    def check_connection(self) -> bool:
        """Pings MongoDB to determine live connectivity."""
        if not self._client:
            self._init_client()
            return self._is_connected

        try:
            self._client.admin.command("ping")
            self._is_connected = True
            return True
        except Exception:
            self._is_connected = False
            return False

    def get_status(self) -> Dict[str, Any]:
        """Returns the actual database connection status and record count."""
        connected = self.check_connection()
        if connected and self._client:
            try:
                db = self._client[self.db_name]
                count = db[self.collection_name].count_documents({})
                return {
                    "status": "connected",
                    "message": f"Connected to live MongoDB at {self.uri}",
                    "uri": self.uri,
                    "db_name": self.db_name,
                    "total_records": count,
                }
            except Exception as e:
                logger.warning("Error fetching count from MongoDB: %s", e)

        # Fallback status
        records = self._read_fallback()
        return {
            "status": "offline_fallback",
            "message": f"MongoDB is offline. Active storage is local fallback at {self.fallback_file.name}",
            "uri": self.uri,
            "db_name": self.db_name,
            "total_records": len(records),
        }

    def save_prediction(self, record: Dict[str, Any]) -> str:
        """
        Saves a prediction record.
        Returns the storage mechanism used: 'mongodb' or 'local_fallback'.
        """
        connected = self.check_connection()
        if connected and self._client:
            try:
                db = self._client[self.db_name]
                col = db[self.collection_name]
                doc = record.copy()
                doc["saved_at"] = datetime.utcnow().isoformat()
                col.insert_one(doc)
                return "mongodb"
            except Exception as e:
                logger.error("Failed writing to MongoDB (%s), using fallback.", e)

        # Write to local fallback
        records = self._read_fallback()
        records.insert(0, record)
        # Keep latest 500 records
        if len(records) > 500:
            records = records[:500]
        self._write_fallback(records)
        return "local_fallback"

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves prediction history, newest first."""
        connected = self.check_connection()
        if connected and self._client:
            try:
                db = self._client[self.db_name]
                col = db[self.collection_name]
                cursor = col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
                results = list(cursor)
                for r in results:
                    r["storage_type"] = "mongodb"
                return results
            except Exception as e:
                logger.warning("Failed reading from MongoDB (%s), reading fallback.", e)

        records = self._read_fallback()
        return records[:limit]

    def clear_history(self) -> int:
        """Clears all records in active storage."""
        count = 0
        if self.check_connection() and self._client:
            try:
                db = self._client[self.db_name]
                res = db[self.collection_name].delete_many({})
                count += res.deleted_count
            except Exception as e:
                logger.warning("Failed clearing MongoDB: %s", e)

        # Also clear fallback
        fallback_records = self._read_fallback()
        count += len(fallback_records)
        self._write_fallback([])
        return count

    def _read_fallback(self) -> List[Dict[str, Any]]:
        try:
            if self.fallback_file.exists():
                with open(self.fallback_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
        except Exception as e:
            logger.error("Error reading fallback file: %s", e)
        return []

    def _write_fallback(self, records: List[Dict[str, Any]]):
        try:
            with open(self.fallback_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            logger.error("Error writing fallback file: %s", e)

# Singleton database manager instance
db_manager = DatabaseManager()
