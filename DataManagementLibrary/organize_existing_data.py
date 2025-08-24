#!/usr/bin/env python3
"""
🗂️ Organize Existing Data Script
Imports and organizes all existing historical data into the Data Management Library
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
from typing import List, Dict, Any

# Add parent path for imports
sys.path.append(str(Path(__file__).parent.parent))

from DataManagementLibrary.core.data_manager import (
    DataManager, DataType, DataSource, DataEntry
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataOrganizer:
    """Organizes existing data into the Data Management Library"""
    
    def __init__(self):
        # Initialize Data Manager with ZmartBot base path
        self.base_path = Path.home() / "Desktop" / "ZmartBot"
        self.dm = DataManager(str(self.base_path / "DataLibrary"))
        self.import_summary = {
            "historical_prices": [],
            "kingfisher_data": [],
            "reports": [],
            "patterns": [],
            "other": []
        }
    
    async def organize_all_data(self):
        """Main function to organize all existing data"""
        print("\n" + "="*60)
        print("🗂️  DATA ORGANIZATION SYSTEM")
        print("="*60)
        print(f"Base Path: {self.base_path}")
        print(f"Data Library: {self.dm.base_path}")
        
        # Step 1: Import Historical Price Data
        await self.import_historical_prices()
        
        # Step 2: Import Kingfisher Data
        await self.import_kingfisher_data()
        
        # Step 3: Import Reports
        await self.import_reports()
        
        # Step 4: Import Database Files
        await self.import_databases()
        
        # Step 5: Create Collections
        await self.create_data_collections()
        
        # Step 6: Generate Summary Report
        self.generate_summary_report()
    
    async def import_historical_prices(self):
        """Import all historical price CSV files"""
        print("\n📊 Importing Historical Price Data...")
        print("-" * 50)
        
        # Check main History Data folder
        history_path = self.base_path / "History Data"
        
        if history_path.exists():
            csv_files = list(history_path.glob("*.csv"))
            print(f"Found {len(csv_files)} CSV files")
            
            for csv_file in csv_files:
                try:
                    # Extract symbol from filename
                    symbol = self._extract_symbol(csv_file.name)
                    
                    # Import the file
                    entry = await self.dm.import_historical_data(
                        str(csv_file),
                        symbol=symbol,
                        data_type=DataType.HISTORICAL_PRICE
                    )
                    
                    self.import_summary["historical_prices"].append({
                        "file": csv_file.name,
                        "symbol": symbol,
                        "entry_id": entry.id
                    })
                    
                    print(f"  ✅ {symbol}: {csv_file.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to import {csv_file.name}: {e}")
                    print(f"  ❌ {csv_file.name}: {str(e)}")
    
    async def import_kingfisher_data(self):
        """Import Kingfisher module data"""
        print("\n🦅 Importing Kingfisher Data...")
        print("-" * 50)
        
        # Check for Kingfisher MD Reports
        kingfisher_path = self.base_path / "kingfisher-module" / "backend" / "downloads" / "MD Reports"
        
        if kingfisher_path.exists():
            md_files = list(kingfisher_path.rglob("*.md"))
            print(f"Found {len(md_files)} Markdown reports")
            
            for md_file in md_files[:10]:  # Limit to first 10 for demo
                try:
                    # Read the markdown content
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract symbol from path or content
                    symbol = self._extract_symbol_from_report(md_file.name, content)
                    
                    # Create data entry
                    entry = DataEntry(
                        id=self.dm._generate_id(symbol, DataType.PROFESSIONAL_REPORT, datetime.now()),
                        symbol=symbol,
                        data_type=DataType.PROFESSIONAL_REPORT,
                        source=DataSource.KINGFISHER,
                        timestamp=datetime.fromtimestamp(md_file.stat().st_mtime),
                        data=content,
                        file_path=str(md_file),
                        checksum=self.dm._calculate_checksum(md_file),
                        metadata={
                            "report_type": "kingfisher_analysis",
                            "file_size": md_file.stat().st_size
                        },
                        tags=["kingfisher", "report", "markdown"]
                    )
                    
                    self.dm._save_entry(entry)
                    self.dm._update_indexes(entry)
                    
                    self.import_summary["kingfisher_data"].append({
                        "file": md_file.name,
                        "symbol": symbol,
                        "entry_id": entry.id
                    })
                    
                    print(f"  ✅ {symbol}: {md_file.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to import {md_file.name}: {e}")
                    print(f"  ❌ {md_file.name}: {str(e)}")
        
        # Check for Kingfisher images
        image_files = list(self.base_path.glob("kingfisher-module/backend/*.jpg"))
        if image_files:
            print(f"\nFound {len(image_files)} Kingfisher images")
            
            for img_file in image_files[:5]:  # Limit for demo
                try:
                    entry = DataEntry(
                        id=self.dm._generate_id("IMAGE", DataType.IMAGE, datetime.now()),
                        symbol="MULTI",
                        data_type=DataType.IMAGE,
                        source=DataSource.KINGFISHER,
                        timestamp=datetime.fromtimestamp(img_file.stat().st_mtime),
                        data=None,  # Don't load binary data
                        file_path=str(img_file),
                        checksum=self.dm._calculate_checksum(img_file),
                        metadata={
                            "image_type": "liquidation_map",
                            "file_size": img_file.stat().st_size
                        },
                        tags=["kingfisher", "image", "liquidation"]
                    )
                    
                    self.dm._save_entry(entry)
                    
                    print(f"  ✅ Image: {img_file.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to import {img_file.name}: {e}")
    
    async def import_reports(self):
        """Import various report files"""
        print("\n📝 Importing Report Files...")
        print("-" * 50)
        
        # Documentation reports
        doc_path = self.base_path / "Documentation"
        
        report_patterns = [
            "*.md",
            "Reports/*.md",
            "Status_Reports/*.md"
        ]
        
        for pattern in report_patterns:
            report_files = list(doc_path.glob(pattern))
            
            for report_file in report_files[:5]:  # Limit for demo
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    entry = DataEntry(
                        id=self.dm._generate_id(report_file.name, DataType.MARKDOWN, datetime.now()),
                        symbol="SYSTEM",
                        data_type=DataType.MARKDOWN,
                        source=DataSource.MANUAL,
                        timestamp=datetime.fromtimestamp(report_file.stat().st_mtime),
                        data=content,
                        file_path=str(report_file),
                        checksum=self.dm._calculate_checksum(report_file),
                        metadata={
                            "report_category": report_file.parent.name,
                            "file_size": report_file.stat().st_size
                        },
                        tags=["documentation", "report"]
                    )
                    
                    self.dm._save_entry(entry)
                    
                    self.import_summary["reports"].append({
                        "file": report_file.name,
                        "category": report_file.parent.name,
                        "entry_id": entry.id
                    })
                    
                    print(f"  ✅ {report_file.parent.name}/{report_file.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to import {report_file.name}: {e}")
    
    async def import_databases(self):
        """Import SQLite database references"""
        print("\n💾 Cataloging Database Files...")
        print("-" * 50)
        
        db_files = list(self.base_path.rglob("*.db"))
        
        print(f"Found {len(db_files)} database files")
        
        for db_file in db_files[:10]:  # Limit for demo
            try:
                entry = DataEntry(
                    id=self.dm._generate_id(db_file.name, "DATABASE", datetime.now()),
                    symbol="DATABASE",
                    data_type=DataType.JSON,  # Using JSON as placeholder
                    source=DataSource.CALCULATED,
                    timestamp=datetime.fromtimestamp(db_file.stat().st_mtime),
                    data=None,
                    file_path=str(db_file),
                    checksum=self.dm._calculate_checksum(db_file),
                    metadata={
                        "database_name": db_file.stem,
                        "file_size": db_file.stat().st_size,
                        "location": str(db_file.parent.relative_to(self.base_path))
                    },
                    tags=["database", "sqlite"]
                )
                
                self.dm._save_entry(entry)
                
                print(f"  ✅ {db_file.parent.name}/{db_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to catalog {db_file.name}: {e}")
    
    async def create_data_collections(self):
        """Create logical collections of related data"""
        print("\n📚 Creating Data Collections...")
        print("-" * 50)
        
        # Create symbol-based collections
        symbols = self.dm.get_statistics()["symbols"]
        
        for symbol in symbols[:5]:  # Limit for demo
            entries = self.dm.search(symbols=[symbol])
            
            if entries:
                collection = self.dm.create_collection(
                    name=f"{symbol}_Complete_Data",
                    description=f"All data entries for {symbol}",
                    entries=entries
                )
                
                print(f"  ✅ Collection: {symbol} ({len(entries)} entries)")
        
        # Create time-based collections
        print("\n  Creating time-based collections...")
        
        # Last 24 hours
        recent_entries = self.dm.search(
            start_date=datetime.now() - pd.Timedelta(days=1)
        )
        
        if recent_entries:
            collection = self.dm.create_collection(
                name="Recent_24h_Data",
                description="All data from the last 24 hours",
                entries=recent_entries
            )
            print(f"  ✅ Recent 24h: {len(recent_entries)} entries")
    
    def generate_summary_report(self):
        """Generate summary report of organized data"""
        print("\n" + "="*60)
        print("📊 DATA ORGANIZATION SUMMARY")
        print("="*60)
        
        # Get statistics
        stats = self.dm.get_statistics()
        
        print(f"\n📈 Overall Statistics:")
        print(f"  • Total Entries: {stats['total_entries']}")
        print(f"  • Unique Symbols: {len(stats['symbols'])}")
        print(f"  • Date Range: {stats['date_range']}")
        print(f"  • Storage Size: {stats['storage_size'] / (1024*1024):.2f} MB")
        
        print(f"\n📁 Data Types:")
        for dt, count in stats['data_types'].items():
            print(f"  • {dt}: {count} entries")
        
        print(f"\n🔗 Data Sources:")
        for source, count in stats['sources'].items():
            print(f"  • {source}: {count} entries")
        
        print(f"\n✅ Import Summary:")
        print(f"  • Historical Prices: {len(self.import_summary['historical_prices'])} files")
        print(f"  • Kingfisher Data: {len(self.import_summary['kingfisher_data'])} files")
        print(f"  • Reports: {len(self.import_summary['reports'])} files")
        
        # Save summary to file
        summary_path = self.dm.directories["reports"] / f"organization_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(summary_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "statistics": stats,
                "import_summary": self.import_summary
            }, f, indent=2, default=str)
        
        print(f"\n💾 Summary saved to: {summary_path}")
        
        # Cleanup duplicates
        print(f"\n🧹 Cleaning up duplicates...")
        removed = self.dm.cleanup_duplicates()
        print(f"  • Removed {removed} duplicate entries")
        
        print("\n✨ Data organization complete!")
    
    def _extract_symbol(self, filename: str) -> str:
        """Extract symbol from filename"""
        # Map of known symbols
        symbol_map = {
            "Bitcoin": "BTC",
            "Ethereum": "ETH",
            "Solana": "SOL",
            "Cardano": "ADA",
            "Polkadot": "DOT",
            "Avalanche": "AVAX",
            "Chainlink": "LINK",
            "Litecoin": "LTC",
            "Dogecoin": "DOGE",
            "Stellar": "XLM",
            "Monero": "XMR",
            "VeChain": "VET",
            "Aave": "AAVE",
            "Render": "RNDR",
            "Sui": "SUI",
            "XRP": "XRP",
            "BNB": "BNB"
        }
        
        # Check filename against map
        for name, symbol in symbol_map.items():
            if name.lower() in filename.lower():
                return symbol
        
        # Try to extract directly
        import re
        patterns = [
            r"([A-Z]{2,5})[-_]",
            r"^([A-Z]{2,5})",
            r"([a-z]{3,5})-usd"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return "UNKNOWN"
    
    def _extract_symbol_from_report(self, filename: str, content: str) -> str:
        """Extract symbol from report filename or content"""
        # Try filename first
        symbol = self._extract_symbol(filename)
        
        if symbol == "UNKNOWN":
            # Try to find in content
            import re
            pattern = r"([A-Z]{2,5})[/-]USDT?"
            match = re.search(pattern, content)
            if match:
                symbol = match.group(1)
        
        return symbol

async def main():
    """Main execution"""
    organizer = DataOrganizer()
    await organizer.organize_all_data()

if __name__ == "__main__":
    asyncio.run(main())