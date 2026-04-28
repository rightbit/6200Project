#!/usr/bin/env python3
"""
Migration script: Import data_exports.json into SQLite database.
Run this if automatic migration during app startup didn't work or if you want to re-migrate.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import from web_app
from web_app import app, db, Export

DATA_EXPORTS_PATH = Path('data_exports.json')


def main():
    if not DATA_EXPORTS_PATH.exists():
        print("✗ data_exports.json not found. Nothing to migrate.")
        return

    try:
        with open(DATA_EXPORTS_PATH, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"✗ Failed to read data_exports.json: {e}")
        return

    exports = data.get('exports', [])
    if not exports:
        print("✗ No exports found in data_exports.json")
        return

    with app.app_context():
        db.create_all()
        migrated = 0

        for item in exports:
            filename = item.get('filename', '')
            if not filename:
                continue

            existing = Export.query.filter_by(filename=filename).first()
            if existing:
                print(f"  ○ Skipping (already in DB): {filename}")
                continue

            try:
                date_str = item.get('date', '')
                if date_str:
                    date_obj = datetime.fromisoformat(date_str)
                else:
                    date_obj = datetime.utcnow()
            except Exception:
                date_obj = datetime.utcnow()

            export_record = Export(
                filename=filename,
                original_name=item.get('original_name'),
                date=date_obj,
                user_type=item.get('user_type'),
                repository=item.get('repository'),
                file_path=item.get('file_path'),
                action=item.get('action'),
            )
            db.session.add(export_record)
            migrated += 1
            print(f"  + Migrated: {filename}")

        db.session.commit()

    print(f"\n✓ Migration complete. {migrated} records imported into the database.")


if __name__ == '__main__':
    main()
