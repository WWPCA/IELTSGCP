"""
DynamoDB to Firestore Migration Script
Migrates all data from AWS DynamoDB Global Tables to Google Cloud Firestore
"""
import boto3
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from firestore_dal import FirestoreConnection
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamoDBToFirestoreMigration:
    """Migrates data from DynamoDB to Firestore"""
    
    def __init__(self, aws_region='us-east-1', gcp_project_id=None):
        self.aws_region = aws_region
        self.gcp_project_id = gcp_project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        
        # Initialize DynamoDB
        self.dynamodb = boto3.resource('dynamodb', region_name=aws_region)
        
        # Initialize Firestore
        self.firestore_conn = FirestoreConnection(project_id=self.gcp_project_id)
        self.db = self.firestore_conn.db
        
        # Table mappings
        stage = os.environ.get('STAGE', 'prod')
        self.table_mappings = {
            f'ielts-genai-prep-users-{stage}': 'users',
            f'ielts-genai-prep-assessments-{stage}': 'assessments',
            f'ielts-genai-prep-sessions-{stage}': 'sessions',
            f'ielts-genai-prep-qr-tokens-{stage}': 'qr_tokens',
            f'ielts-genai-prep-entitlements-{stage}': 'entitlements',
        }
        
        logger.info(f"Initialized migration: AWS {aws_region} → GCP {gcp_project_id}")
    
    def convert_dynamodb_to_firestore(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB item format to Firestore document format"""
        converted = {}
        
        for key, value in item.items():
            # Convert DynamoDB types to Python types
            if isinstance(value, str):
                # Check if it's an ISO datetime string
                if 'T' in value and (value.endswith('Z') or '+' in value or '-' in value[-6:]):
                    try:
                        converted[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except:
                        converted[key] = value
                else:
                    converted[key] = value
            elif isinstance(value, (int, float, bool)):
                converted[key] = value
            elif isinstance(value, dict):
                converted[key] = self.convert_dynamodb_to_firestore(value)
            elif isinstance(value, list):
                converted[key] = [self.convert_dynamodb_to_firestore(v) if isinstance(v, dict) else v for v in value]
            elif value is None:
                converted[key] = None
            else:
                converted[key] = str(value)
        
        return converted
    
    def migrate_table(self, dynamodb_table_name: str, firestore_collection_name: str) -> Dict[str, int]:
        """Migrate a single table from DynamoDB to Firestore"""
        logger.info(f"Migrating {dynamodb_table_name} → {firestore_collection_name}")
        
        try:
            table = self.dynamodb.Table(dynamodb_table_name)
            collection = self.db.collection(firestore_collection_name)
            
            # Scan DynamoDB table
            response = table.scan()
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            logger.info(f"Found {len(items)} items in {dynamodb_table_name}")
            
            # Batch write to Firestore
            batch = self.db.batch()
            batch_count = 0
            migrated_count = 0
            
            for item in items:
                # Convert DynamoDB item to Firestore document
                doc_data = self.convert_dynamodb_to_firestore(item)
                
                # Determine document ID
                if firestore_collection_name == 'users':
                    doc_id = doc_data.get('email', f"user_{migrated_count}")
                elif firestore_collection_name == 'assessments':
                    doc_id = doc_data.get('assessment_id', f"assess_{migrated_count}")
                elif firestore_collection_name == 'sessions':
                    doc_id = doc_data.get('session_id', f"session_{migrated_count}")
                elif firestore_collection_name == 'qr_tokens':
                    doc_id = doc_data.get('token', f"qr_{migrated_count}")
                elif firestore_collection_name == 'entitlements':
                    doc_id = doc_data.get('entitlement_id', f"ent_{migrated_count}")
                else:
                    doc_id = f"doc_{migrated_count}"
                
                # Add to batch
                doc_ref = collection.document(doc_id)
                batch.set(doc_ref, doc_data)
                
                batch_count += 1
                migrated_count += 1
                
                # Firestore batch limit is 500
                if batch_count >= 500:
                    batch.commit()
                    batch = self.db.batch()
                    batch_count = 0
                    logger.info(f"  Migrated {migrated_count}/{len(items)} items...")
            
            # Commit remaining items
            if batch_count > 0:
                batch.commit()
            
            logger.info(f"✓ Successfully migrated {migrated_count} items from {dynamodb_table_name}")
            
            return {
                'total': len(items),
                'migrated': migrated_count,
                'skipped': len(items) - migrated_count
            }
            
        except Exception as e:
            logger.error(f"✗ Failed to migrate {dynamodb_table_name}: {e}")
            return {
                'total': 0,
                'migrated': 0,
                'skipped': 0,
                'error': str(e)
            }
    
    def migrate_all(self) -> Dict[str, Any]:
        """Migrate all tables from DynamoDB to Firestore"""
        logger.info("Starting full migration...")
        
        results = {}
        total_migrated = 0
        
        for dynamodb_table, firestore_collection in self.table_mappings.items():
            result = self.migrate_table(dynamodb_table, firestore_collection)
            results[firestore_collection] = result
            total_migrated += result.get('migrated', 0)
        
        logger.info(f"\n{'='*60}")
        logger.info("Migration Summary:")
        logger.info(f"{'='*60}")
        
        for collection, result in results.items():
            if 'error' in result:
                logger.error(f"  {collection}: ERROR - {result['error']}")
            else:
                logger.info(f"  {collection}: {result['migrated']}/{result['total']} migrated")
        
        logger.info(f"{'='*60}")
        logger.info(f"Total items migrated: {total_migrated}")
        logger.info(f"{'='*60}\n")
        
        return results
    
    def verify_migration(self) -> Dict[str, bool]:
        """Verify migration by comparing record counts"""
        logger.info("Verifying migration...")
        
        verification = {}
        stage = os.environ.get('STAGE', 'prod')
        
        for dynamodb_table, firestore_collection in self.table_mappings.items():
            try:
                # Count DynamoDB items
                table = self.dynamodb.Table(dynamodb_table)
                response = table.scan(Select='COUNT')
                dynamodb_count = response.get('Count', 0)
                
                # Count Firestore documents
                collection_ref = self.db.collection(firestore_collection)
                firestore_count = len(list(collection_ref.stream()))
                
                match = dynamodb_count == firestore_count
                verification[firestore_collection] = {
                    'dynamodb_count': dynamodb_count,
                    'firestore_count': firestore_count,
                    'match': match
                }
                
                status = "✓" if match else "✗"
                logger.info(f"{status} {firestore_collection}: DynamoDB={dynamodb_count}, Firestore={firestore_count}")
                
            except Exception as e:
                logger.error(f"✗ Verification failed for {firestore_collection}: {e}")
                verification[firestore_collection] = {
                    'error': str(e),
                    'match': False
                }
        
        return verification


def main():
    """Run migration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate DynamoDB to Firestore')
    parser.add_argument('--aws-region', default='us-east-1', help='AWS region')
    parser.add_argument('--gcp-project', default=None, help='GCP project ID')
    parser.add_argument('--verify-only', action='store_true', help='Only verify existing migration')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no writes)')
    
    args = parser.parse_args()
    
    # Initialize migration
    migrator = DynamoDBToFirestoreMigration(
        aws_region=args.aws_region,
        gcp_project_id=args.gcp_project
    )
    
    if args.verify_only:
        # Verification only
        verification = migrator.verify_migration()
        all_match = all(v.get('match', False) for v in verification.values())
        
        if all_match:
            logger.info("\n✓ Migration verified successfully!")
            sys.exit(0)
        else:
            logger.error("\n✗ Migration verification failed!")
            sys.exit(1)
    else:
        # Run migration
        if args.dry_run:
            logger.warning("DRY RUN MODE - No data will be written")
            # TODO: Implement dry run logic
        else:
            results = migrator.migrate_all()
            
            # Verify
            logger.info("\nVerifying migration...")
            verification = migrator.verify_migration()
            
            all_match = all(v.get('match', False) for v in verification.values())
            
            if all_match:
                logger.info("\n✓ Migration completed and verified successfully!")
                sys.exit(0)
            else:
                logger.warning("\n⚠ Migration completed but verification found mismatches")
                sys.exit(1)


if __name__ == '__main__':
    main()
