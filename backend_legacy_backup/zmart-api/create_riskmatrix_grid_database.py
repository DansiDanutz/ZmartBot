#!/usr/bin/env python3
"""
Create RiskMatrixGrid Database
Exact copy of Google Sheets data for frontend display
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RiskMatrixGridDatabase:
    """Create and populate RiskMatrixGrid database"""
    
    def __init__(self, db_path="data/RiskMatrixGrid.db"):
        self.db_path = db_path
        
        # Complete Google Sheets data (August 12, 2025)
        self.risk_matrix_data = {
            'BTC': [30000.00, 31352.00, 32704.00, 34055.00, 35567.00, 37452.00, 39336.00, 41718.00, 44371.00, 47457.00, 50778.00, 54471.00, 58519.00, 62865.00, 67523.00, 72497.00, 77786.00, 83389.00, 89306.00, 95537.00, 102082.00, 108941.00, 116114.00, 123601.00, 131402.00, 139517.00, 147946.00, 156689.00, 165746.00, 175117.00, 184802.00, 194801.00, 205114.00, 215741.00, 226682.00, 237937.00, 249506.00, 261389.00, 273586.00, 286097.00, 299720.00],
            'ETH': [445.60, 482.55, 522.56, 565.88, 612.80, 663.60, 718.62, 778.20, 842.72, 912.59, 988.25, 1070.19, 1158.92, 1255.00, 1359.05, 1471.73, 1593.75, 1725.61, 1867.31, 2018.85, 2180.23, 2351.45, 2532.51, 2723.41, 2924.15, 3134.73, 3355.15, 3585.41, 3825.51, 4075.45, 4335.23, 4604.85, 4884.31, 5173.61, 5472.75, 5781.73, 6100.55, 6429.21, 6767.71, 7116.05, 7474.23],
            'XRP': [0.78, 0.81, 0.85, 0.89, 0.93, 0.97, 1.02, 1.07, 1.12, 1.17, 1.22, 1.28, 1.34, 1.40, 1.46, 1.53, 1.60, 1.67, 1.74, 1.81, 1.88, 1.95, 2.02, 2.09, 2.16, 2.23, 2.30, 2.37, 2.44, 2.51, 2.58, 2.65, 2.72, 2.79, 2.86, 2.93, 3.00, 3.07, 3.14, 3.21, 3.28],
            'BNB': [279.62, 293.96, 309.04, 324.88, 341.60, 359.23, 377.75, 397.32, 417.93, 439.58, 462.44, 486.63, 511.87, 538.61, 566.99, 596.86, 628.52, 661.95, 697.25, 734.52, 773.86, 815.37, 859.15, 905.30, 953.92, 1005.11, 1058.97, 1115.60, 1175.10, 1237.57, 1303.11, 1371.82, 1443.80, 1519.15, 1597.97, 1680.36, 1766.42, 1856.25, 1949.95, 2047.62, 2149.36],
            'SOL': [18.75, 21.09, 23.69, 26.64, 29.92, 33.64, 37.81, 42.50, 47.76, 53.73, 60.40, 68.04, 76.82, 82.68, 87.78, 93.25, 99.00, 105.03, 111.34, 117.93, 124.80, 131.95, 139.38, 147.09, 155.08, 163.35, 171.90, 180.73, 189.84, 199.23, 208.90, 218.85, 229.08, 239.59, 250.38, 261.45, 272.80, 284.43, 296.34, 308.53, 321.00],
            'DOGE': [0.07, 0.07, 0.07, 0.08, 0.08, 0.09, 0.10, 0.10, 0.11, 0.12, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40, 0.41, 0.42],
            'ADA': [0.10, 0.11, 0.12, 0.14, 0.15, 0.17, 0.19, 0.22, 0.24, 0.27, 0.31, 0.35, 0.39, 0.45, 0.50, 0.53, 0.56, 0.59, 0.62, 0.65, 0.68, 0.71, 0.74, 0.77, 0.80, 0.83, 0.86, 0.89, 0.92, 0.95, 0.98, 1.01, 1.04, 1.07, 1.10, 1.13, 1.16, 1.19, 1.22, 1.25, 1.28],
            'LINK': [2.34, 2.61, 2.92, 3.26, 3.65, 4.08, 4.57, 5.12, 5.73, 6.41, 7.19, 8.06, 9.04, 10.14, 10.81, 11.44, 12.11, 12.82, 13.57, 14.36, 15.19, 16.06, 16.97, 17.92, 18.91, 19.94, 21.01, 22.12, 23.27, 24.46, 25.69, 26.96, 28.27, 29.62, 31.01, 32.44, 33.91, 35.42, 36.97, 38.56, 40.19],
            'AVAX': [4.14, 4.67, 5.26, 5.93, 6.69, 7.54, 8.50, 9.58, 10.80, 12.19, 13.75, 15.50, 17.47, 19.69, 21.21, 22.53, 23.94, 25.44, 27.03, 28.71, 30.48, 32.34, 34.29, 36.33, 38.46, 40.68, 42.99, 45.39, 47.88, 50.46, 53.13, 55.89, 58.74, 61.68, 64.71, 67.83, 71.04, 74.34, 77.73, 81.21, 84.78],
            'XLM': [0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48],
            'SUI': [1.25, 1.40, 1.57, 1.75, 1.87, 1.97, 2.09, 2.21, 2.33, 2.47, 2.61, 2.76, 2.92, 3.09, 3.28, 3.49, 3.73, 3.99, 4.27, 4.58, 4.91, 5.27, 5.66, 6.08, 6.53, 7.01, 7.52, 8.07, 8.66, 9.29, 9.96, 10.67, 11.42, 12.21, 13.04, 13.91, 14.82, 15.77, 16.76, 17.79, 18.86],
            'DOT': [1.48, 1.67, 1.89, 2.13, 2.40, 2.70, 3.05, 3.44, 3.81, 4.05, 4.31, 4.58, 4.86, 5.17, 5.50, 5.84, 6.21, 6.60, 7.01, 7.44, 7.89, 8.36, 8.85, 9.36, 9.89, 10.44, 11.01, 11.60, 12.21, 12.84, 13.49, 14.16, 14.85, 15.56, 16.29, 17.04, 17.81, 18.60, 19.41, 20.24, 21.09],
            'LTC': [18.52, 20.72, 23.19, 26.00, 29.17, 32.72, 36.76, 41.27, 46.39, 52.19, 58.70, 65.04, 68.93, 73.02, 77.39, 82.02, 86.92, 92.09, 97.53, 103.14, 108.92, 114.87, 120.99, 127.28, 133.74, 140.37, 147.17, 154.14, 161.28, 168.59, 176.07, 183.72, 191.54, 199.53, 207.69, 216.02, 224.52, 233.19, 242.03, 251.04, 260.22],
            'XMR': [78.61, 87.48, 97.25, 108.25, 117.23, 123.63, 130.36, 137.49, 145.01, 152.98, 161.34, 170.15, 179.47, 189.29, 199.68, 210.62, 222.18, 234.37, 247.20, 260.67, 274.78, 289.53, 304.92, 320.95, 337.62, 354.93, 372.88, 391.47, 410.70, 430.57, 451.08, 472.23, 494.02, 516.45, 539.52, 563.23, 587.58, 612.57, 638.20, 664.47, 691.38],
            'AAVE': [63.35, 70.10, 77.57, 85.89, 95.00, 105.22, 116.53, 125.90, 132.40, 139.27, 146.49, 154.13, 162.15, 170.59, 179.49, 188.86, 198.69, 208.98, 219.73, 230.94, 242.61, 254.74, 267.33, 280.38, 293.89, 307.86, 322.29, 337.18, 352.53, 368.34, 384.61, 401.34, 418.53, 436.18, 454.29, 472.86, 491.89, 511.38, 531.33, 551.74, 572.61],
            'VET': [0.01, 0.01, 0.01, 0.02, 0.02, 0.02, 0.02, 0.02, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.07, 0.07, 0.07, 0.07, 0.07, 0.07, 0.08, 0.08, 0.08],
            'ATOM': [1.75, 1.97, 2.21, 2.49, 2.80, 3.15, 3.54, 3.98, 4.41, 4.68, 4.97, 5.27, 5.59, 5.94, 6.30, 6.69, 6.97, 7.26, 7.56, 7.87, 8.19, 8.52, 8.86, 9.21, 9.57, 9.94, 10.32, 10.71, 11.11, 11.52, 11.94, 12.37, 12.81, 13.26, 13.72, 14.19, 14.67, 15.16, 15.66, 16.17, 16.69],
            'RENDER': [1.06, 1.18, 1.32, 1.47, 1.65, 1.84, 2.06, 2.30, 2.57, 2.84, 3.00, 3.18, 3.36, 3.55, 3.76, 3.97, 4.19, 4.42, 4.66, 4.91, 5.17, 5.44, 5.72, 6.01, 6.31, 6.62, 6.94, 7.27, 7.61, 7.96, 8.32, 8.69, 9.07, 9.46, 9.86, 10.27, 10.69, 11.12, 11.56, 12.01, 12.47],
            'HBAR': [0.06, 0.07, 0.08, 0.09, 0.09, 0.10, 0.11, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40, 0.41, 0.42, 0.43],
            'XTZ': [0.48, 0.53, 0.58, 0.62, 0.65, 0.68, 0.72, 0.75, 0.79, 0.83, 0.87, 0.91, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50, 1.55, 1.60, 1.65, 1.70, 1.75, 1.80, 1.85, 1.90, 1.95, 2.00, 2.05, 2.10, 2.15, 2.20, 2.25, 2.30, 2.35],
            'TON': [1.49, 1.63, 1.79, 1.95, 2.14, 2.34, 2.56, 2.80, 3.03, 3.17, 3.31, 3.47, 3.63, 3.79, 3.97, 4.15, 4.34, 4.53, 4.73, 4.93, 5.14, 5.35, 5.57, 5.79, 6.02, 6.25, 6.49, 6.73, 6.98, 7.23, 7.49, 7.75, 8.02, 8.29, 8.57, 8.85, 9.14, 9.43, 9.73, 10.03, 10.34],
            'TRX': [0.10, 0.10, 0.11, 0.11, 0.12, 0.12, 0.13, 0.13, 0.14, 0.14, 0.15, 0.15, 0.16, 0.16, 0.17, 0.17, 0.18, 0.18, 0.19, 0.19, 0.20, 0.20, 0.21, 0.21, 0.22, 0.22, 0.23, 0.23, 0.24, 0.24, 0.25, 0.25, 0.26, 0.26, 0.27, 0.27, 0.28, 0.28, 0.29, 0.29, 0.30]
        }
        
        # Risk values (0.0 to 1.0 in 0.025 increments)
        self.risk_values = [round(i * 0.025, 3) for i in range(41)]

    def create_database(self):
        """Create the RiskMatrixGrid database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create the risk matrix table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_matrix_grid (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    risk_value REAL NOT NULL,
                    btc_price REAL,
                    eth_price REAL,
                    xrp_price REAL,
                    bnb_price REAL,
                    sol_price REAL,
                    doge_price REAL,
                    ada_price REAL,
                    link_price REAL,
                    avax_price REAL,
                    xlm_price REAL,
                    sui_price REAL,
                    dot_price REAL,
                    ltc_price REAL,
                    xmr_price REAL,
                    aave_price REAL,
                    vet_price REAL,
                    atom_price REAL,
                    render_price REAL,
                    hbar_price REAL,
                    xtz_price REAL,
                    ton_price REAL,
                    trx_price REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for fast lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_risk_value ON risk_matrix_grid(risk_value)')
            
            conn.commit()
            logger.info(f"✅ Created RiskMatrixGrid database: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def populate_database(self):
        """Populate the database with complete risk matrix data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute('DELETE FROM risk_matrix_grid')
            
            # Insert all risk levels
            for i, risk_value in enumerate(self.risk_values):
                row_data = [risk_value]
                
                # Add prices for each symbol
                for symbol in self.risk_matrix_data.keys():
                    price = self.risk_matrix_data[symbol][i]
                    row_data.append(price)
                
                # Insert the row
                placeholders = ','.join(['?' for _ in range(len(row_data))])
                cursor.execute(f'''
                    INSERT INTO risk_matrix_grid 
                    (risk_value, btc_price, eth_price, xrp_price, bnb_price, sol_price, 
                     doge_price, ada_price, link_price, avax_price, xlm_price, sui_price, 
                     dot_price, ltc_price, xmr_price, aave_price, vet_price, atom_price, 
                     render_price, hbar_price, xtz_price, ton_price, trx_price)
                    VALUES ({placeholders})
                ''', row_data)
            
            conn.commit()
            logger.info(f"✅ Populated {len(self.risk_values)} risk levels with {len(self.risk_matrix_data)} symbols")
            
        except Exception as e:
            logger.error(f"Error populating database: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def get_all_data(self):
        """Get all risk matrix data for frontend display"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM risk_matrix_grid ORDER BY risk_value')
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute('PRAGMA table_info(risk_matrix_grid)')
            columns = [col[1] for col in cursor.fetchall()]
            
            conn.close()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = {}
                for i, col_name in enumerate(columns):
                    row_dict[col_name] = row[i]
                data.append(row_dict)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting data: {e}")
            return []

def main():
    logger.info("🚀 Creating RiskMatrixGrid Database")
    
    db = RiskMatrixGridDatabase()
    
    # Create database
    db.create_database()
    
    # Populate with data
    db.populate_database()
    
    # Test data retrieval
    data = db.get_all_data()
    logger.info(f"✅ Retrieved {len(data)} rows from database")
    
    logger.info("🎉 RiskMatrixGrid database creation completed!")

if __name__ == "__main__":
    main()
