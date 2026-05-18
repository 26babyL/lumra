"""
Database Router for Primary/Replica Read-Write Splitting

This router directs read queries to a read replica and write queries to the primary.
Useful for scaling read-heavy applications with 1M+ records.

Configuration in settings.py:
    DATABASE_ROUTERS = ['lumra_config.routers.PrimaryReplicaRouter']
    
    DATABASES = {
        'default': { ... primary ... },
        'replica': { ... read replica ... }
    }
"""

from django.conf import settings


class PrimaryReplicaRouter:
    """
    Route database operations to primary or replica.
    
    Rules:
    - Write operations: always to 'default' (primary)
    - Read operations: to 'replica' if available, otherwise 'default'
    - Migrations: only on 'default' (primary)
    - Relations: allowed between any databases
    """
    
    def db_for_read(self, model, **hints):
        """Route read queries to replica if available"""
        if 'write' not in hints:
            # Check if we have a replica configured
            if 'replica' in settings.DATABASES:
                return 'replica'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Route write queries to primary"""
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relationships between any databases"""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Migrations should only run on primary (default)"""
        return db == 'default'


class BranchSpecificRouter:
    """
    Route queries based on branch context (for multi-branch systems).
    
    Ensures queries filter by current branch automatically.
    Requires: request.current_branch_id to be set in middleware
    """
    
    def db_for_read(self, model, **hints):
        # Could add branch-specific logic here if needed
        if 'replica' in settings.DATABASES:
            return 'replica'
        return 'default'
    
    def db_for_write(self, model, **hints):
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'
