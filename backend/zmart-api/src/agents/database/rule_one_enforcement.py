"""
Rule #1 Enforcement for RiskMetric Database Agent

CRITICAL RULE: Database Agent CANNOT modify BTC min/max foundation values.
Only Admin can set these values programmatically and from frontend.

This module enforces Rule #1 by:
1. Blocking Database Agent access to BTC foundation modifications
2. Providing read-only access to BTC foundation values
3. Logging any attempted violations
4. Redirecting BTC foundation operations to Admin-only endpoints
"""

import logging
from typing import Dict, Any, Optional
from functools import wraps
import sqlite3
import os

logger = logging.getLogger(__name__)

class RuleOneViolationError(Exception):
    """Raised when Rule #1 is violated."""
    pass

class RuleOneEnforcer:
    """Enforces Rule #1 restrictions on Database Agent."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.btc_foundation_table = "btc_foundation_values"
    
    def get_current_btc_foundation(self) -> Dict[str, Any]:
        """Get current BTC foundation values (READ-ONLY for Database Agent)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                SELECT risk_zero_price, risk_one_price, price_range, updated_at
                FROM {self.btc_foundation_table} 
                WHERE is_active = 1 
                ORDER BY updated_at DESC 
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            if result:
                risk_zero, risk_one, price_range, updated_at = result
                return {
                    "risk_zero_price": risk_zero,
                    "risk_one_price": risk_one,
                    "price_range": price_range,
                    "updated_at": updated_at,
                    "access_level": "READ_ONLY",
                    "rule_status": "Rule #1 enforced - Database Agent cannot modify these values"
                }
            else:
                # Return default values if none found
                return {
                    "risk_zero_price": 30000.0,
                    "risk_one_price": 279514.0,
                    "price_range": 249514.0,
                    "updated_at": None,
                    "access_level": "READ_ONLY",
                    "rule_status": "Default values - Rule #1 enforced"
                }
                
        except Exception as e:
            logger.error(f"Error getting BTC foundation (read-only): {e}")
            # Return safe defaults
            return {
                "risk_zero_price": 30000.0,
                "risk_one_price": 279514.0,
                "price_range": 249514.0,
                "updated_at": None,
                "access_level": "READ_ONLY",
                "error": str(e)
            }
        finally:
            conn.close()
    
    def validate_btc_operation(self, operation_name: str, **kwargs) -> None:
        """Validate if Database Agent can perform BTC-related operation."""
        
        # Operations that are PROHIBITED for Database Agent
        prohibited_operations = [
            "update_btc_foundation",
            "modify_btc_min_max",
            "set_btc_risk_zero",
            "set_btc_risk_one",
            "initialize_bitcoin_risk_grid",  # If it modifies foundation
            "update_btc_foundation_values"
        ]
        
        if operation_name in prohibited_operations:
            error_msg = f"RULE #1 VIOLATION: Database Agent cannot perform '{operation_name}'. Only Admin can modify BTC foundation values."
            logger.error(error_msg)
            raise RuleOneViolationError(error_msg)
        
        # Log allowed operations for audit
        logger.info(f"Rule #1 check passed: Database Agent performing allowed operation '{operation_name}'")
    
    def get_btc_grid_for_calculations(self) -> Dict[str, Any]:
        """Get BTC risk grid for calculations (READ-ONLY)."""
        foundation = self.get_current_btc_foundation()
        
        # Generate grid based on current foundation values
        risk_levels = [i * 0.025 for i in range(41)]  # 0.000 to 1.000
        min_price = foundation["risk_zero_price"]
        max_price = foundation["risk_one_price"]
        price_range = max_price - min_price
        
        grid_data = {}
        for risk in risk_levels:
            price = min_price + (risk * price_range)
            grid_data[risk] = {
                "price": price,
                "access_level": "READ_ONLY"
            }
        
        return {
            "grid_data": grid_data,
            "foundation": foundation,
            "total_bands": len(risk_levels),
            "rule_status": "Rule #1 enforced - READ-ONLY access"
        }

def enforce_rule_one(operation_name: str):
    """Decorator to enforce Rule #1 on Database Agent methods."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Check if this is a Database Agent instance
            if hasattr(self, 'db_path') and hasattr(self, 'core_db'):
                rule_enforcer = RuleOneEnforcer(self.db_path)
                
                try:
                    # Validate the operation
                    rule_enforcer.validate_btc_operation(operation_name, **kwargs)
                    
                    # If validation passes, execute the function
                    return await func(self, *args, **kwargs)
                    
                except RuleOneViolationError as e:
                    # Return error instead of executing prohibited operation
                    return {
                        "error": str(e),
                        "rule_violation": True,
                        "rule_number": 1,
                        "admin_required": True,
                        "redirect_to": "/api/v1/admin-riskmetric/btc-foundation/"
                    }
            else:
                # Not a Database Agent, execute normally
                return await func(self, *args, **kwargs)
        
        return wrapper
    return decorator

def btc_read_only_access(func):
    """Decorator to provide read-only access to BTC foundation data."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if hasattr(self, 'db_path'):
            rule_enforcer = RuleOneEnforcer(self.db_path)
            
            # Add BTC foundation data to kwargs for read-only access
            kwargs['btc_foundation'] = rule_enforcer.get_current_btc_foundation()
            kwargs['btc_grid'] = rule_enforcer.get_btc_grid_for_calculations()
            
            logger.info(f"Rule #1: Providing read-only BTC data to {func.__name__}")
        
        return await func(self, *args, **kwargs)
    
    return wrapper

class DatabaseAgentRuleOneWrapper:
    """Wrapper to enforce Rule #1 on Database Agent methods."""
    
    def __init__(self, database_agent):
        self.agent = database_agent
        self.rule_enforcer = RuleOneEnforcer(database_agent.db_path)
        self.logger = logging.getLogger(__name__)
    
    async def safe_initialize_bitcoin_risk_grid(self, **kwargs) -> Dict[str, Any]:
        """Safe wrapper for Bitcoin grid initialization - uses foundation values."""
        try:
            # Get current foundation values (read-only)
            foundation = self.rule_enforcer.get_current_btc_foundation()
            
            # Use foundation values instead of allowing modification
            grid_data = {}
            risk_levels = [i * 0.025 for i in range(41)]
            
            min_price = foundation["risk_zero_price"]
            max_price = foundation["risk_one_price"]
            price_range = max_price - min_price
            
            for risk in risk_levels:
                price = min_price + (risk * price_range)
                grid_data[risk] = {
                    "min_price": price,
                    "max_price": price + (price_range * 0.025) if risk < 1.0 else price
                }
            
            # Update the database grid with foundation-based values
            conn = sqlite3.connect(self.agent.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM btc_risk_grid')
                
                for risk, data in grid_data.items():
                    cursor.execute('''
                        INSERT INTO btc_risk_grid (risk_level, min_price, max_price, updated_at)
                        VALUES (?, ?, ?, datetime('now'))
                    ''', (risk, data["min_price"], data["max_price"]))
                
                conn.commit()
                
                self.logger.info(f"Rule #1: Bitcoin grid updated using foundation values (Risk 0: ${min_price}, Risk 1: ${max_price})")
                
                return {
                    "success": True,
                    "message": "Bitcoin risk grid updated using foundation values",
                    "foundation_used": foundation,
                    "bands_updated": len(grid_data),
                    "rule_status": "Rule #1 enforced - used existing foundation values"
                }
                
            except Exception as e:
                self.logger.error(f"Error updating Bitcoin grid with foundation values: {e}")
                return {"error": str(e)}
            finally:
                conn.close()
                
        except Exception as e:
            self.logger.error(f"Rule #1 enforcement error: {e}")
            return {
                "error": str(e),
                "rule_status": "Rule #1 enforcement failed"
            }
    
    def get_btc_foundation_readonly(self) -> Dict[str, Any]:
        """Get BTC foundation values for Database Agent (read-only)."""
        return self.rule_enforcer.get_current_btc_foundation()