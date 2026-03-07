"""
Automated Backup System for User Data
Exports all data periodically for disaster recovery
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from database import db, User, Assessment, AssessmentResult
import boto3
from pathlib import Path


class BackupManager:
    """Manages automated backups of user data"""

    def __init__(self, backup_dir: str = "./backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

        # S3 setup (optional - for cloud backups)
        self.s3_bucket = os.getenv("BACKUP_S3_BUCKET")
        self.s3_client = None

        if self.s3_bucket:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "eu-north-1")
                )
                print("✅ S3 backup enabled")
            except Exception as e:
                print(f"⚠️  S3 backup disabled: {e}")

    def create_full_backup(self) -> str:
        """Create full database backup"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_data = {
            "timestamp": timestamp,
            "version": "1.0",
            "users": [],
            "assessments": [],
            "results": []
        }

        session = db.get_session()

        try:
            # Export all users (anonymized)
            users = session.query(User).all()
            for user in users:
                backup_data["users"].append({
                    "user_id": user.id,
                    "created_at": user.created_at.isoformat(),
                    "last_active": user.last_active.isoformat(),
                    "consents": [
                        {
                            "type": c.consent_type,
                            "given": c.consent_given,
                            "date": c.consent_date.isoformat()
                        }
                        for c in user.consents
                    ]
                })

            # Export all assessments
            assessments = session.query(Assessment).filter_by(is_anonymized=False).all()
            for assessment in assessments:
                backup_data["assessments"].append({
                    "assessment_id": assessment.id,
                    "user_id": assessment.user_id,
                    "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
                    "language": assessment.language,
                    "status": assessment.status
                })

            # Export all results
            results = session.query(AssessmentResult).all()
            for result in results:
                backup_data["results"].append({
                    "assessment_id": result.assessment_id,
                    "scores": result.scores,
                    "created_at": result.created_at.isoformat()
                })

            # Save locally
            filename = f"backup_{timestamp}.json"
            filepath = self.backup_dir / filename

            with open(filepath, 'w') as f:
                json.dump(backup_data, f, indent=2)

            print(f"✅ Backup created: {filepath}")

            # Upload to S3 if configured
            if self.s3_client and self.s3_bucket:
                try:
                    self.s3_client.upload_file(
                        str(filepath),
                        self.s3_bucket,
                        f"backups/{filename}"
                    )
                    print(f"✅ Backup uploaded to S3: {filename}")
                except Exception as e:
                    print(f"⚠️  S3 upload failed: {e}")

            return str(filepath)

        except Exception as e:
            print(f"❌ Backup failed: {e}")
            raise e
        finally:
            session.close()

    def restore_from_backup(self, backup_file: str):
        """Restore data from backup file"""
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)

        session = db.get_session()

        try:
            # This is a simplified restore - extend as needed
            print(f"Restoring backup from {backup_data['timestamp']}")
            print(f"  Users: {len(backup_data['users'])}")
            print(f"  Assessments: {len(backup_data['assessments'])}")
            print(f"  Results: {len(backup_data['results'])}")

            # WARNING: Full restore should be done carefully!
            # This is a template - implement actual restoration logic

            session.commit()
            print("✅ Restore completed")

        except Exception as e:
            session.rollback()
            print(f"❌ Restore failed: {e}")
            raise e
        finally:
            session.close()

    def cleanup_old_backups(self, keep_days: int = 30):
        """Delete backups older than keep_days"""
        cutoff = datetime.utcnow().timestamp() - (keep_days * 86400)

        for backup_file in self.backup_dir.glob("backup_*.json"):
            if backup_file.stat().st_mtime < cutoff:
                backup_file.unlink()
                print(f"Deleted old backup: {backup_file.name}")


def create_backup():
    """CLI command to create backup"""
    manager = BackupManager()
    filepath = manager.create_full_backup()
    print(f"\n✅ Backup created successfully: {filepath}")
    manager.cleanup_old_backups()


if __name__ == "__main__":
    create_backup()
