"""SQLite audit trail and compliance governance for DemandWise.

Persists immutable logs of:
- Dataset ingestion & schema validation
- Forecasting model executions & accuracy metrics
- Hierarchical reconciliation runs & coherence verification
- Inventory simulation decisions & policy scenarios
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pandas as pd


@dataclass
class AuditRecord:
    """Represents an immutable event entry in the audit database."""

    event_type: str  # 'DATA_INGESTION', 'FORECAST_RUN', 'RECONCILIATION', 'INVENTORY_RUN'
    action: str
    details: Dict[str, Any]
    status: str = "SUCCESS"  # 'SUCCESS', 'WARNING', 'ERROR'
    actor: str = "DemandWise_Engine"
    timestamp: str = ""
    record_hash: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.record_hash:
            payload = f"{self.timestamp}|{self.event_type}|{self.action}|{json.dumps(self.details, sort_keys=True)}"
            self.record_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class AuditLogger:
    """Manages the local SQLite audit log database."""

    def __init__(self, db_path: str = "artifacts/demandwise_audit.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Create audit log schema if it does not already exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    record_hash TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_logs(event_type);
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
                """
            )
            conn.commit()

    def log_event(
        self,
        event_type: str,
        action: str,
        details: Dict[str, Any],
        status: str = "SUCCESS",
        actor: str = "DemandWise_Engine",
    ) -> AuditRecord:
        """Record an event to the audit trail."""
        record = AuditRecord(
            event_type=event_type,
            action=action,
            details=details,
            status=status,
            actor=actor,
        )
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_logs (timestamp, event_type, action, status, actor, details_json, record_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.timestamp,
                    record.event_type,
                    record.action,
                    record.status,
                    record.actor,
                    json.dumps(record.details),
                    record.record_hash,
                ),
            )
            conn.commit()
        return record

    def get_recent_logs(self, limit: int = 50, event_type: Optional[str] = None) -> pd.DataFrame:
        """Retrieve recent audit logs as a DataFrame."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT id, timestamp, event_type, action, status, actor, details_json, record_hash FROM audit_logs"
            params = []
            if event_type:
                query += " WHERE event_type = ?"
                params.append(event_type)
            query += " ORDER BY id DESC LIMIT ?"
            params.append(limit)
            df = pd.read_sql_query(query, conn, params=params)
        return df
