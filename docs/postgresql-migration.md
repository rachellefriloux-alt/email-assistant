# PostgreSQL Migration Guide

This guide walks you through migrating from SQLite to PostgreSQL for production deployments.

## Prerequisites

- PostgreSQL 12+ installed and running
- Database user with CREATE DATABASE privileges
- Access to your application environment variables

## Step 1: Install PostgreSQL Client

The `psycopg2-binary` package is already included in `requirements.txt`. If you need to reinstall:

```bash
pip install psycopg2-binary==2.9.9
```

## Step 2: Create PostgreSQL Database

Connect to PostgreSQL and create a new database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE email_assistant;

# Create user (optional, if not using existing user)
CREATE USER email_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE email_assistant TO email_user;

# Exit
\q
```

## Step 3: Update Environment Variables

Update your `.env` file or environment configuration with the PostgreSQL connection string:

### SQLite (Current - Development)
```env
DATABASE_URL=sqlite:///./emails.db
```

### PostgreSQL (Production)
```env
DATABASE_URL=postgresql://email_user:your_secure_password@localhost:5432/email_assistant
```

For cloud PostgreSQL services:
- **AWS RDS**: `postgresql://user:pass@db-instance.region.rds.amazonaws.com:5432/email_assistant`
- **Google Cloud SQL**: `postgresql://user:pass@/database?host=/cloudsql/project:region:instance`
- **Heroku**: `postgresql://user:pass@host.compute.amazonaws.com:5432/database`
- **DigitalOcean**: `postgresql://user:pass@db-postgresql-region-do-user-cluster.db.ondigitalocean.com:25060/email_assistant?sslmode=require`

## Step 4: Initialize Database Schema

The application uses SQLModel which automatically creates tables on startup. Simply start your application with the new DATABASE_URL:

```bash
# Backend will create all tables on startup
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

The `init_db()` function in `db.py` will automatically create all tables based on your models.

## Step 5: Migrate Existing Data (Optional)

If you have existing data in SQLite that you want to migrate:

### Option A: Manual Export/Import

1. Export data from SQLite:
```bash
sqlite3 emails.db .dump > dump.sql
```

2. Clean up SQLite-specific syntax and import to PostgreSQL:
```bash
# Remove SQLite-specific statements
sed -i '/PRAGMA/d' dump.sql
sed -i 's/AUTOINCREMENT/SERIAL/g' dump.sql

# Import to PostgreSQL
psql -U email_user -d email_assistant -f dump.sql
```

### Option B: Using Python Script

Create a migration script `migrate_data.py`:

```python
import os
from sqlmodel import Session, create_engine, select
from models.email import EmailRecord
from models.account import Account
from models.template import Template

# Source (SQLite)
sqlite_engine = create_engine("sqlite:///./emails.db")

# Destination (PostgreSQL)
postgres_url = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/email_assistant")
postgres_engine = create_engine(postgres_url)

# Migrate emails
with Session(sqlite_engine) as src_session:
    with Session(postgres_engine) as dst_session:
        # Migrate EmailRecord
        emails = src_session.exec(select(EmailRecord)).all()
        for email in emails:
            dst_session.add(EmailRecord(**email.model_dump(exclude={'id'})))
        
        # Migrate other models as needed
        dst_session.commit()

print("Migration completed!")
```

Run the migration:
```bash
python migrate_data.py
```

## Step 6: Using Alembic for Schema Migrations (Recommended)

For production environments, use Alembic for schema version control:

### Initialize Alembic (if not already done)

```bash
cd backend
alembic init alembic
```

### Configure Alembic

Edit `alembic.ini`:
```ini
sqlalchemy.url = postgresql://user:pass@localhost/email_assistant
```

Or use environment variable in `alembic/env.py`:
```python
from os import environ
config.set_main_option('sqlalchemy.url', environ.get('DATABASE_URL'))
```

### Create Initial Migration

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Future Schema Changes

When you modify models:
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Step 7: Performance Optimization

### Create Indexes

For better query performance, create indexes:

```sql
-- Indexes on EmailRecord
CREATE INDEX idx_emailrecord_account_id ON emailrecord(account_id);
CREATE INDEX idx_emailrecord_gmail_id ON emailrecord(gmail_id);
CREATE INDEX idx_emailrecord_from_email ON emailrecord(from_email);
CREATE INDEX idx_emailrecord_category ON emailrecord(category);
CREATE INDEX idx_emailrecord_status ON emailrecord(status);
CREATE INDEX idx_emailrecord_created_at ON emailrecord(created_at DESC);

-- Full-text search index (PostgreSQL specific)
CREATE INDEX idx_emailrecord_search ON emailrecord USING gin(to_tsvector('english', subject || ' ' || body_text));

-- Indexes on Account
CREATE INDEX idx_account_email ON account(email);

-- Indexes on Template
CREATE INDEX idx_template_category ON template(category);
CREATE INDEX idx_template_account_id ON template(account_id);
```

### Connection Pooling

For production, configure connection pooling in `db.py`:

```python
from sqlmodel import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Number of connections to maintain
    max_overflow=10,        # Additional connections if needed
    pool_pre_ping=True,     # Verify connections before using
    pool_recycle=3600,      # Recycle connections after 1 hour
)
```

## Step 8: Backup Strategy

### Automated Backups

Set up automated PostgreSQL backups:

```bash
# Daily backup script
pg_dump -U email_user email_assistant | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore from backup
gunzip < backup_20231201.sql.gz | psql -U email_user email_assistant
```

### Continuous Backup (WAL archiving)

Enable Point-in-Time Recovery (PITR) in `postgresql.conf`:

```conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'
```

## Step 9: Security Considerations

1. **Use SSL/TLS**: Add `?sslmode=require` to your DATABASE_URL
2. **Strong passwords**: Use complex passwords for database users
3. **Network security**: Restrict PostgreSQL access via firewall rules
4. **Encrypt credentials**: Use environment variables or secret management systems
5. **Rotate passwords**: Regularly update database credentials

## Step 10: Monitoring

Monitor PostgreSQL performance:

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check database size
SELECT pg_size_pretty(pg_database_size('email_assistant'));
```

## Rollback Plan

If you need to rollback to SQLite:

1. Stop the application
2. Change DATABASE_URL back to SQLite
3. Restore data from backup if needed
4. Restart the application

## Docker Compose with PostgreSQL

Update `docker-compose.yml` to include PostgreSQL:

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: email_assistant
      POSTGRES_USER: email_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://email_user:your_secure_password@postgres:5432/email_assistant
    depends_on:
      - postgres

volumes:
  postgres_data:
```

## Testing the Migration

1. Verify connection:
```bash
psql postgresql://user:pass@localhost/email_assistant -c "SELECT version();"
```

2. Check tables:
```sql
\dt
```

3. Test application:
```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/gmail/list
```

## Common Issues

### Issue: "Peer authentication failed"
**Solution**: Edit `pg_hba.conf` to use `md5` instead of `peer`:
```
local   all   all   md5
```

### Issue: Connection refused
**Solution**: Check if PostgreSQL is running and accepting connections:
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Issue: "SSL connection required"
**Solution**: Add `?sslmode=require` or `?sslmode=disable` to DATABASE_URL

### Issue: Performance slower than SQLite
**Solution**: Ensure indexes are created and connection pooling is configured

## Support

For additional help:
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Alembic Documentation: https://alembic.sqlalchemy.org/
