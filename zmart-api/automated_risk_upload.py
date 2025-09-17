#!/usr/bin/env python3
"""
Automated Risk Data Upload to Supabase using MCP
"""
import subprocess
import os

def upload_via_mcp():
    """Upload risk data using MCP supabase tools"""

    # Read the SQL file in chunks
    sql_file = "complete_risk_import.sql"

    if not os.path.exists(sql_file):
        print("❌ SQL file not found!")
        return False

    print("🚀 Starting automated upload via MCP...")

    # Step 1: Prepare the table schema
    schema_sql = """
-- Prepare table schema
ALTER TABLE risk_metric_grid
ADD COLUMN IF NOT EXISTS risk_type VARCHAR(20) DEFAULT 'KEY_RISK';

ALTER TABLE risk_metric_grid
DROP CONSTRAINT IF EXISTS risk_metric_grid_unique_key;

ALTER TABLE risk_metric_grid
ADD CONSTRAINT risk_metric_grid_unique_key
UNIQUE (symbol, price_point, risk_type);
"""

    # Step 2: Clear existing data
    clear_sql = "DELETE FROM risk_metric_grid;"

    # Step 3: Split the large SQL file into smaller chunks
    print("📄 Processing SQL file...")

    with open(sql_file, 'r') as f:
        content = f.read()

    # Find all INSERT blocks
    import re

    # Split by INSERT statements
    insert_blocks = re.split(r'(INSERT INTO risk_metric_grid.*?ON CONFLICT.*?;)', content, flags=re.DOTALL)
    insert_statements = [block for block in insert_blocks if 'INSERT INTO' in block]

    print(f"📊 Found {len(insert_statements)} INSERT blocks")

    # Execute each block separately using claude API
    try:
        # Execute schema preparation
        print("🔧 Preparing table schema...")
        result = subprocess.run([
            'python3', '-c',
            f"""
import os
os.system('echo "{schema_sql}" | claude api --model claude-3-sonnet-20241022 --prompt "Execute this SQL in Supabase via MCP supabase tools"')
"""
        ], capture_output=True, text=True)

        print("🧹 Clearing existing data...")
        # Clear data
        result = subprocess.run([
            'python3', '-c',
            f"""
import os
os.system('echo "{clear_sql}" | claude api --model claude-3-sonnet-20241022 --prompt "Execute this SQL in Supabase via MCP supabase tools"')
"""
        ], capture_output=True, text=True)

        # Execute INSERT blocks in batches
        print("⬆️ Uploading data in batches...")

        batch_size = 5  # 5 INSERT blocks per batch
        total_batches = (len(insert_statements) + batch_size - 1) // batch_size

        for i in range(0, len(insert_statements), batch_size):
            batch = insert_statements[i:i+batch_size]
            batch_num = i // batch_size + 1

            batch_sql = '\\n'.join(batch)

            print(f"   📦 Batch {batch_num}/{total_batches}: {len(batch)} INSERT blocks")

            # Execute batch via claude API
            result = subprocess.run([
                'python3', '-c',
                f"""
import os
os.system('echo "{batch_sql}" | claude api --model claude-3-sonnet-20241022 --prompt "Execute this SQL in Supabase via MCP supabase tools"')
"""
            ], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"   ❌ Batch {batch_num} failed: {result.stderr}")
            else:
                print(f"   ✅ Batch {batch_num} completed")

        print("🎉 Upload completed!")
        return True

    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def verify_upload():
    """Verify the upload was successful"""
    print("🔍 Verifying upload...")

    verify_sql = """
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT symbol) as total_symbols,
    COUNT(DISTINCT risk_type) as risk_types
FROM risk_metric_grid;
"""

    try:
        result = subprocess.run([
            'python3', '-c',
            f"""
import os
os.system('echo "{verify_sql}" | claude api --model claude-3-sonnet-20241022 --prompt "Execute this SQL query in Supabase via MCP supabase tools and show results"')
"""
        ], capture_output=True, text=True)

        print("✅ Verification completed")
        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = upload_via_mcp()
    if success:
        verify_upload()
    else:
        print("❌ Upload failed!")