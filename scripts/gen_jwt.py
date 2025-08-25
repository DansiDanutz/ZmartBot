#!/usr/bin/env python3
"""
JWT Token Generator for KingFisher Testing
Generates JWT tokens for development, testing, and CI environments
"""

import argparse
import os
import jwt
import time
import json
from typing import List

def generate_token(
    subject: str,
    roles: List[str],
    permissions: List[str] = None,
    secret: str = None,
    expires_in_hours: int = 24,
    algorithm: str = "HS256"
) -> str:
    """Generate JWT token with specified claims"""
    
    if secret is None:
        secret = os.getenv("SERVICE_TOKEN_SECRET", "kingfisher-dev-secret-change-in-prod")
    
    if permissions is None:
        permissions = roles  # Default: permissions same as roles
    
    current_time = int(time.time())
    
    payload = {
        "sub": subject,
        "roles": roles,
        "permissions": permissions,
        "iat": current_time,
        "exp": current_time + (expires_in_hours * 3600),
        "iss": "kingfisher-token-generator",
        "aud": "zmart-kingfisher"
    }
    
    return jwt.encode(payload, secret, algorithm=algorithm)

def validate_token(token: str, secret: str = None) -> dict:
    """Validate and decode JWT token"""
    
    if secret is None:
        secret = os.getenv("SERVICE_TOKEN_SECRET", "kingfisher-dev-secret-change-in-prod")
    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return {"valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token expired"}
    except jwt.InvalidTokenError as e:
        return {"valid": False, "error": str(e)}

def print_token_info(token: str):
    """Print token information without validation"""
    try:
        # Decode without verification to see payload
        payload = jwt.decode(token, options={"verify_signature": False})
        
        print(f"Subject: {payload.get('sub', 'N/A')}")
        print(f"Roles: {', '.join(payload.get('roles', []))}")
        print(f"Permissions: {', '.join(payload.get('permissions', []))}")
        print(f"Issued At: {time.ctime(payload.get('iat', 0))}")
        print(f"Expires At: {time.ctime(payload.get('exp', 0))}")
        print(f"Issuer: {payload.get('iss', 'N/A')}")
        print(f"Audience: {payload.get('aud', 'N/A')}")
        
    except Exception as e:
        print(f"Error decoding token: {e}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="JWT Token Generator for KingFisher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate admin token
  python gen_jwt.py --roles admin

  # Generate analysis token with custom expiry
  python gen_jwt.py --roles analysis.read,analysis.write --expires 48

  # Generate service token
  python gen_jwt.py --subject kingfisher-ci --roles admin --type service

  # Validate existing token
  python gen_jwt.py --validate "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

  # Generate multiple tokens at once
  python gen_jwt.py --preset ci-tokens

Environment Variables:
  SERVICE_TOKEN_SECRET: Secret key for signing tokens (required for production)
        """
    )
    
    parser.add_argument("--roles", type=str,
                       help="Comma-separated list of roles (e.g., admin,analysis.read)")
    parser.add_argument("--permissions", type=str,
                       help="Comma-separated list of permissions (defaults to roles)")
    parser.add_argument("--subject", default="kingfisher-user",
                       help="Token subject (default: kingfisher-user)")
    parser.add_argument("--expires", type=int, default=24,
                       help="Expiry time in hours (default: 24)")
    parser.add_argument("--secret", type=str,
                       help="JWT secret (uses SERVICE_TOKEN_SECRET env var by default)")
    parser.add_argument("--validate", type=str,
                       help="Validate and decode existing JWT token")
    parser.add_argument("--info", type=str,
                       help="Show token info without validation")
    parser.add_argument("--preset", type=str, choices=["ci-tokens", "dev-tokens", "all-roles"],
                       help="Generate preset token combinations")
    parser.add_argument("--type", choices=["user", "service"], default="user",
                       help="Token type (affects subject naming)")
    parser.add_argument("--output", choices=["token", "env", "json"], default="token",
                       help="Output format")
    parser.add_argument("--quiet", action="store_true",
                       help="Only output the token (no extra text)")
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("🔐 KingFisher JWT Token Generator v1.1.0")
    
    # Validation mode
    if args.validate:
        result = validate_token(args.validate, args.secret)
        
        if result["valid"]:
            if not args.quiet:
                print("✅ Token is valid")
                print_token_info(args.validate)
        else:
            print(f"❌ Token validation failed: {result['error']}")
            exit(1)
        return
    
    # Info mode
    if args.info:
        if not args.quiet:
            print("ℹ️ Token Information (unverified):")
        print_token_info(args.info)
        return
    
    # Preset mode
    if args.preset:
        if args.preset == "ci-tokens":
            tokens = {
                "ADMIN_TOKEN": generate_token("kingfisher-ci", ["admin"], expires_in_hours=2),
                "WRITE_TOKEN": generate_token("kingfisher-ci", ["analysis.write"], expires_in_hours=2),
                "READ_TOKEN": generate_token("kingfisher-ci", ["analysis.read"], expires_in_hours=2)
            }
        elif args.preset == "dev-tokens":
            tokens = {
                "DEV_ADMIN_TOKEN": generate_token("kingfisher-dev", ["admin"], expires_in_hours=24),
                "DEV_USER_TOKEN": generate_token("kingfisher-dev", ["analysis.read", "analysis.write"], expires_in_hours=24)
            }
        elif args.preset == "all-roles":
            tokens = {
                "ADMIN_TOKEN": generate_token("kingfisher-admin", ["admin"]),
                "WRITE_TOKEN": generate_token("kingfisher-writer", ["analysis.write"]),
                "READ_TOKEN": generate_token("kingfisher-reader", ["analysis.read"]),
                "SERVICE_TOKEN": generate_token("kingfisher-service", ["admin"], expires_in_hours=24*7)
            }
        
        if args.output == "env":
            for name, token in tokens.items():
                print(f'export {name}="{token}"')
        elif args.output == "json":
            print(json.dumps(tokens, indent=2))
        else:
            for name, token in tokens.items():
                if not args.quiet:
                    print(f"{name}:")
                print(token)
                if not args.quiet:
                    print()
        return
    
    # Single token generation
    if not args.roles:
        print("❌ --roles required (or use --preset)")
        exit(1)
    
    roles = [role.strip() for role in args.roles.split(",")]
    permissions = [perm.strip() for perm in args.permissions.split(",")] if args.permissions else roles
    
    # Adjust subject based on type
    if args.type == "service":
        subject = f"{args.subject}-service" if not args.subject.endswith("-service") else args.subject
    else:
        subject = args.subject
    
    token = generate_token(
        subject=subject,
        roles=roles,
        permissions=permissions,
        secret=args.secret,
        expires_in_hours=args.expires
    )
    
    if args.output == "env":
        token_name = "TOKEN" if len(roles) == 1 else "MULTI_TOKEN"
        print(f'export {token_name}="{token}"')
    elif args.output == "json":
        token_info = {
            "token": token,
            "subject": subject,
            "roles": roles,
            "permissions": permissions,
            "expires_in_hours": args.expires,
            "type": args.type
        }
        print(json.dumps(token_info, indent=2))
    else:
        if not args.quiet:
            print(f"✅ Generated {args.type} token:")
            print(f"   Subject: {subject}")
            print(f"   Roles: {', '.join(roles)}")
            print(f"   Permissions: {', '.join(permissions)}")
            print(f"   Expires: {args.expires} hours")
            print()
        print(token)

if __name__ == "__main__":
    main()