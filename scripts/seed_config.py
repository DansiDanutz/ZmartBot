#!/usr/bin/env python3
"""
Config Seeding Utility for KingFisher Service
Seeds configuration data for dev/staging/prod environments
"""

import argparse
import json
import hashlib
import os
import sys
import psycopg2
import psycopg2.extras
from typing import Dict, Any

def get_db_connection():
    """Get database connection from environment variables"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST", "localhost"),
            database=os.getenv("PG_DB", "zmart_core"),
            user=os.getenv("PG_USER", "zmart"),
            password=os.getenv("PG_PASS", "zmart"),
            port=os.getenv("PG_PORT", "5432")
        )
        return conn
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        print("Environment variables needed:")
        print("  PG_HOST (default: localhost)")
        print("  PG_DB (default: zmart_core)")
        print("  PG_USER (default: zmart)")
        print("  PG_PASS (default: zmart)")
        print("  PG_PORT (default: 5432)")
        sys.exit(1)

def ensure_config_table(conn):
    """Ensure the configuration table exists"""
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS config_entries (
                id SERIAL PRIMARY KEY,
                service_name VARCHAR(100) NOT NULL,
                env VARCHAR(20) NOT NULL,
                version VARCHAR(20) NOT NULL DEFAULT 'v1',
                data JSONB NOT NULL,
                etag VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(service_name, env, version)
            )
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_config_service_env 
            ON config_entries(service_name, env)
        """)
        
        conn.commit()
        cur.close()
        print("✅ Config table ensured")
    except psycopg2.Error as e:
        print(f"❌ Failed to create config table: {e}")
        sys.exit(1)

def calculate_etag(data: Dict[str, Any]) -> str:
    """Calculate ETag for configuration data"""
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    hash_digest = hashlib.sha256(json_str.encode()).hexdigest()
    return f'W/"{hash_digest}"'

def upsert_config(conn, service_name: str, env: str, data: Dict[str, Any], version: str = "v1"):
    """Insert or update configuration entry"""
    try:
        etag = calculate_etag(data)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO config_entries(service_name, env, version, data, etag, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT (service_name, env, version) 
            DO UPDATE SET 
                data = EXCLUDED.data,
                etag = EXCLUDED.etag,
                updated_at = NOW()
            RETURNING id, created_at, updated_at
        """, (service_name, env, version, json.dumps(data), etag))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        
        if result:
            print(f"✅ Config updated for {service_name}:{env} (id: {result[0]})")
            return True
        else:
            print(f"❌ Failed to update config for {service_name}:{env}")
            return False
            
    except psycopg2.Error as e:
        print(f"❌ Failed to upsert config: {e}")
        conn.rollback()
        return False

def get_kingfisher_config(env: str) -> Dict[str, Any]:
    """Get KingFisher configuration for specific environment"""
    
    # Base configuration
    base_config = {
        "features": {
            "enable_plugin_finalize": True,
            "enable_realtime_price": True,
            "enable_perceptual_hashing": True,
            "enable_security_middleware": True,
            "enable_transactional_outbox": True
        },
        "duplicate": {
            "phash_threshold": 5,
            "dhash_threshold": 5,
            "use_md5_prefilter": True,
            "batch_size": 100
        },
        "orchestrator": {
            "max_workers": 4,
            "queue_maxsize": 100,
            "timeout_seconds": 300,
            "retry_attempts": 3
        },
        "openai": {
            "max_qps": 2,
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000,
            "timeout_seconds": 30
        },
        "idempotency": {
            "ttl_hours": 24,
            "cleanup_interval_hours": 6
        },
        "storage": {
            "images_root": "data/images",
            "tmp_ttl_hours": 72,
            "max_file_size_mb": 10,
            "allowed_extensions": [".jpg", ".jpeg", ".png", ".gif"]
        },
        "security": {
            "rate_limits": {
                "default": {"requests": 100, "window": 60},
                "upload": {"requests": 10, "window": 60},
                "ai": {"requests": 30, "window": 60}
            },
            "jwt": {
                "algorithm": "HS256",
                "expiry_hours": 24
            }
        },
        "outbox": {
            "publisher_interval_seconds": 5,
            "max_retry_attempts": 5,
            "cleanup_after_days": 7,
            "batch_size": 100
        },
        "step5": {
            "order": [
                "plugins.symbol_update",
                "plugins.extract_liq_clusters", 
                "plugins.real_market_price",
                "plugins.finalize"
            ],
            "continue_on_error": True,
            "timeout_per_plugin": 60
        },
        "monitoring": {
            "metrics_enabled": True,
            "tracing_enabled": True,
            "log_level": "INFO",
            "health_check_interval": 30
        },
        "integrations": {
            "telegram": {
                "enabled": True,
                "rate_limit_per_hour": 30,
                "timeout_seconds": 10
            },
            "airtable": {
                "enabled": True,
                "rate_limit_per_minute": 5,
                "timeout_seconds": 15
            },
            "binance": {
                "enabled": True,
                "rate_limit_per_minute": 1200,
                "timeout_seconds": 10
            }
        }
    }
    
    # Environment-specific overrides
    if env == "dev":
        base_config.update({
            "monitoring": {
                **base_config["monitoring"],
                "log_level": "DEBUG"
            },
            "features": {
                **base_config["features"],
                "enable_security_middleware": False  # Easier for dev
            }
        })
    
    elif env == "staging":
        base_config.update({
            "orchestrator": {
                **base_config["orchestrator"],
                "max_workers": 6
            },
            "openai": {
                **base_config["openai"],
                "max_qps": 4
            },
            "security": {
                **base_config["security"],
                "rate_limits": {
                    "default": {"requests": 200, "window": 60},
                    "upload": {"requests": 20, "window": 60},
                    "ai": {"requests": 50, "window": 60}
                }
            }
        })
    
    elif env == "prod":
        base_config.update({
            "orchestrator": {
                **base_config["orchestrator"],
                "max_workers": 8,
                "queue_maxsize": 500
            },
            "openai": {
                **base_config["openai"],
                "max_qps": 8,
                "timeout_seconds": 45
            },
            "security": {
                **base_config["security"],
                "rate_limits": {
                    "default": {"requests": 500, "window": 60},
                    "upload": {"requests": 50, "window": 60},
                    "ai": {"requests": 100, "window": 60}
                }
            },
            "idempotency": {
                **base_config["idempotency"],
                "ttl_hours": 48  # Longer retention in prod
            },
            "monitoring": {
                **base_config["monitoring"],
                "log_level": "WARNING",  # Less verbose in prod
                "health_check_interval": 15
            }
        })
    
    return base_config

def seed_all_environments(service_name: str):
    """Seed configuration for all environments"""
    environments = ["dev", "staging", "prod"]
    conn = get_db_connection()
    
    try:
        ensure_config_table(conn)
        
        success_count = 0
        for env in environments:
            print(f"\n📦 Seeding {service_name} config for {env}...")
            config = get_kingfisher_config(env)
            
            if upsert_config(conn, service_name, env, config):
                success_count += 1
                print(f"   - Features: {len(config['features'])} enabled")
                print(f"   - Max workers: {config['orchestrator']['max_workers']}")
                print(f"   - OpenAI QPS: {config['openai']['max_qps']}")
                print(f"   - Rate limits: {config['security']['rate_limits']['default']['requests']} req/min")
            else:
                print(f"❌ Failed to seed {env} config")
        
        print(f"\n🎯 Seeded {success_count}/{len(environments)} environments successfully")
        
    finally:
        conn.close()

def validate_config(service_name: str, env: str):
    """Validate existing configuration"""
    conn = get_db_connection()
    
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT service_name, env, version, data, etag, updated_at
            FROM config_entries 
            WHERE service_name = %s AND env = %s
            ORDER BY version DESC
        """, (service_name, env))
        
        rows = cur.fetchall()
        cur.close()
        
        if not rows:
            print(f"❌ No configuration found for {service_name}:{env}")
            return False
        
        for row in rows:
            config_data = row['data']
            print(f"\n✅ Configuration for {service_name}:{env} (version: {row['version']})")
            print(f"   Updated: {row['updated_at']}")
            print(f"   ETag: {row['etag']}")
            print(f"   Features: {list(config_data.get('features', {}).keys())}")
            print(f"   Plugins: {len(config_data.get('step5', {}).get('order', []))}")
            
            # Validate required sections
            required_sections = ["features", "orchestrator", "security", "step5"]
            missing_sections = [s for s in required_sections if s not in config_data]
            
            if missing_sections:
                print(f"   ⚠️ Missing sections: {missing_sections}")
            else:
                print(f"   ✅ All required sections present")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Validation failed: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Config seeding utility for KingFisher service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Seed single environment
  python seed_config.py --env dev --service zmart-kingfisher
  
  # Seed all environments
  python seed_config.py --service zmart-kingfisher --all-envs
  
  # Validate existing config
  python seed_config.py --service zmart-kingfisher --env prod --validate
  
  # Custom service with JSON config
  python seed_config.py --service my-service --env dev --config config.json
        """
    )
    
    parser.add_argument("--service", required=True, 
                       help="Service name (e.g., zmart-kingfisher)")
    parser.add_argument("--env", choices=["dev", "staging", "prod"],
                       help="Environment to seed")
    parser.add_argument("--all-envs", action="store_true",
                       help="Seed all environments (dev, staging, prod)")
    parser.add_argument("--validate", action="store_true",
                       help="Validate existing configuration")
    parser.add_argument("--config", type=str,
                       help="Path to custom config JSON file")
    parser.add_argument("--version", default="v1",
                       help="Config version (default: v1)")
    
    args = parser.parse_args()
    
    print(f"🔧 KingFisher Config Seeder v1.1.0")
    print(f"Service: {args.service}")
    
    # Validation mode
    if args.validate:
        if not args.env:
            print("❌ --env required for validation")
            sys.exit(1)
        success = validate_config(args.service, args.env)
        sys.exit(0 if success else 1)
    
    # All environments mode
    if args.all_envs:
        if args.service != "zmart-kingfisher":
            print("❌ --all-envs only supported for zmart-kingfisher")
            sys.exit(1)
        seed_all_environments(args.service)
        return
    
    # Single environment mode
    if not args.env:
        print("❌ --env required (or use --all-envs)")
        sys.exit(1)
    
    conn = get_db_connection()
    
    try:
        ensure_config_table(conn)
        
        # Custom config file
        if args.config:
            if not os.path.exists(args.config):
                print(f"❌ Config file not found: {args.config}")
                sys.exit(1)
            
            with open(args.config, 'r') as f:
                config_data = json.load(f)
            
            print(f"📁 Using custom config from {args.config}")
        else:
            # Built-in KingFisher config
            config_data = get_kingfisher_config(args.env)
            print(f"📦 Using built-in KingFisher config for {args.env}")
        
        success = upsert_config(conn, args.service, args.env, config_data, args.version)
        
        if success:
            print(f"✅ Configuration seeded successfully")
            print(f"   Service: {args.service}")
            print(f"   Environment: {args.env}")
            print(f"   Version: {args.version}")
            print(f"   Features: {len(config_data.get('features', {}))}")
        else:
            print(f"❌ Failed to seed configuration")
            sys.exit(1)
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()