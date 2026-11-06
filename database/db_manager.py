
import sqlite3
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "inspection_history.db"


def get_connection():
    """Create a connection to the inspection database."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                image_filename TEXT NOT NULL,
                processing_status TEXT NOT NULL,
                od_px REAL,
                id_px REAL,
                od_mm REAL,
                id_mm REAL,
                measurement_status TEXT,
                center_difference_px REAL,
                id_od_ratio REAL,
                defect_detection_status TEXT NOT NULL,
                inspection_orientation TEXT NOT NULL DEFAULT 'vertical'
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(inspections)"
            ).fetchall()
        }

        migrations = {
            "inspection_orientation": (
                "ALTER TABLE inspections ADD COLUMN "
                "inspection_orientation TEXT NOT NULL DEFAULT 'vertical'"
            ),
            "od_mm": "ALTER TABLE inspections ADD COLUMN od_mm REAL",
            "id_mm": "ALTER TABLE inspections ADD COLUMN id_mm REAL",
        }

        for column, sql in migrations.items():
            if column not in columns:
                connection.execute(sql)


def save_inspection(
    image_filename,
    processing_status,
    od_px=None,
    id_px=None,
    od_mm=None,
    id_mm=None,
    measurement_status=None,
    center_difference_px=None,
    id_od_ratio=None,
    defect_detection_status="NOT_IMPLEMENTED",
    inspection_orientation="vertical",
):
    initialize_database()

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    orientation = str(inspection_orientation).lower()

    if orientation not in ("vertical", "horizontal"):
        raise ValueError(
            "inspection_orientation must be 'vertical' or 'horizontal'"
        )

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO inspections (
                timestamp,
                image_filename,
                processing_status,
                od_px,
                id_px,
                od_mm,
                id_mm,
                measurement_status,
                center_difference_px,
                id_od_ratio,
                defect_detection_status,
                inspection_orientation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            str(image_filename),
            str(processing_status),
            od_px,
            id_px,
            od_mm,
            id_mm,
            measurement_status,
            center_difference_px,
            id_od_ratio,
            str(defect_detection_status),
            orientation,
        ))

        return cursor.lastrowid


def get_inspection_history(limit=500):
    """Return the most recent inspection records."""
    initialize_database()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM inspections
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()

    return [dict(row) for row in rows]


def get_inspection_statistics():
    """Return overall inspection and measurement statistics."""
    initialize_database()

    with get_connection() as connection:
        row = connection.execute("""
            SELECT
                COUNT(*) AS total_inspections,
                SUM(
                    CASE
                        WHEN processing_status = 'completed'
                        THEN 1 ELSE 0
                    END
                ) AS completed_inspections,
                SUM(
                    CASE
                        WHEN processing_status != 'completed'
                        THEN 1 ELSE 0
                    END
                ) AS failed_inspections
            FROM inspections
        """).fetchone()

    return {
        "total_inspections": row["total_inspections"] or 0,
        "completed_inspections": row["completed_inspections"] or 0,
        "failed_inspections": row["failed_inspections"] or 0,
    }
