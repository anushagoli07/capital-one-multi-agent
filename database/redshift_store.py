import json
import os
from typing import Dict, Any

class RedshiftStore:
    def __init__(self, table_name: str = "financial_kpis"):
        self.table_name = table_name
        self.storage_path = os.environ.get('KPI_STORAGE_PATH', 'database/kpi_records.json')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Initialize storage if it doesn't exist
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)

    def insert_kpis(self, kpi_data: Dict[str, Any]):
        """
        Simulates inserting KPIs into a Redshift table.
        Saves to a local JSON file for demonstration.
        """
        print(f"Inserting KPIs into Redshift table '{self.table_name}'...")
        
        with open(self.storage_path, 'r') as f:
            records = json.load(f)
            
        records.append(kpi_data)
        
        with open(self.storage_path, 'w') as f:
            json.dump(records, f, indent=4)
            
        print(f"Successfully stored KPIs for {kpi_data.get('fiscal_year')}")

    def fetch_all_kpis(self):
        """
        Fetches all stored KPIs.
        """
        with open(self.storage_path, 'r') as f:
            return json.load(f)
            
    def query_kpi_by_year(self, year: int):
        """
        Queries KPIs for a specific year.
        """
        records = self.fetch_all_kpis()
        return [r for r in records if r.get('fiscal_year') == year]
