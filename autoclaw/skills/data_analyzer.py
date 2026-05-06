"""
AutoClaw - Autonomous AI Agent Platform
Data Analyzer Skill

Reads and analyzes CSV, JSON, Excel files. Creates visualizations.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

SKILL_METADATA = {
    "name": "data_analyzer",
    "version": "1.0.0",
    "description": "Data analysis: parse CSV/JSON/Excel, statistics, visualizations",
    "author": "AutoClaw Team",
    "capabilities": [
        "read_csv",
        "read_json",
        "read_excel",
        "analyze_statistics",
        "create_chart",
        "filter_data",
        "export_data"
    ]
}


class DataAnalyzer:
    """Data analysis operations."""
    
    def __init__(self):
        self.loaded_datasets = {}
        self.analysis_results = []
    
    async def read_csv(self, path: str, delimiter: str = ",", has_header: bool = True) -> Dict:
        """Read a CSV file."""
        try:
            file_path = Path(path)
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            rows = []
            headers = None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if has_header:
                    reader = csv.reader(f, delimiter=delimiter)
                    headers = next(reader)
                    for row in reader:
                        if len(row) == len(headers):
                            rows.append(dict(zip(headers, row)))
                else:
                    reader = csv.reader(f, delimiter=delimiter)
                    for i, row in enumerate(reader):
                        rows.append({f"col_{i}": row})
            
            dataset_id = f"csv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.loaded_datasets[dataset_id] = {
                "type": "csv",
                "headers": headers,
                "rows": rows,
                "source": str(file_path)
            }
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "row_count": len(rows),
                "columns": headers or list(range(len(rows[0]) if rows else 0)),
                "preview": rows[:5],
                "message": f"Loaded {len(rows)} rows from {file_path.name}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def read_json(self, path: str) -> Dict:
        """Read a JSON file."""
        try:
            file_path = Path(path)
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                data = [{"value": data}]
            
            dataset_id = f"json_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            headers = list(data[0].keys()) if data else []
            
            self.loaded_datasets[dataset_id] = {
                "type": "json",
                "headers": headers,
                "rows": data,
                "source": str(file_path)
            }
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "row_count": len(data),
                "columns": headers,
                "preview": data[:5],
                "message": f"Loaded {len(data)} records from {file_path.name}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def read_excel(self, path: str, sheet: Optional[str] = None) -> Dict:
        """Read an Excel file."""
        try:
            try:
                from openpyxl import load_workbook
                
                wb = load_workbook(filename=path, read_only=True)
                ws = wb[sheet] if sheet else wb.active
                
                rows = []
                headers = None
                
                for i, row in enumerate(ws.iter_rows(values_only=True)):
                    if i == 0:
                        headers = [str(cell) if cell else f"col_{j}" for j, cell in enumerate(row)]
                    else:
                        if any(cell is not None for cell in row):
                            row_dict = {headers[j]: str(cell) if cell else "" for j, cell in enumerate(row)}
                            rows.append(row_dict)
                
                wb.close()
                
            except ImportError:
                return {"success": False, "error": "openpyxl not installed"}
            
            dataset_id = f"excel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.loaded_datasets[dataset_id] = {
                "type": "excel",
                "headers": headers,
                "rows": rows,
                "source": str(path)
            }
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "row_count": len(rows),
                "columns": headers,
                "preview": rows[:5],
                "message": f"Loaded {len(rows)} rows from Excel"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def analyze_statistics(self, dataset_id: str, columns: Optional[List[str]] = None) -> Dict:
        """Perform statistical analysis on a dataset."""
        if dataset_id not in self.loaded_datasets:
            return {"success": False, "error": f"Dataset not found: {dataset_id}"}
        
        dataset = self.loaded_datasets[dataset_id]
        rows = dataset["rows"]
        
        if not columns:
            columns = dataset["headers"]
        
        stats = {}
        
        for col in columns:
            values = [row.get(col) for row in rows if row.get(col) is not None]
            
            if not values:
                continue
            
            numeric_values = []
            for v in values:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass
            
            if numeric_values:
                numeric_values.sort()
                n = len(numeric_values)
                stats[col] = {
                    "type": "numeric",
                    "count": n,
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "mean": sum(numeric_values) / n,
                    "median": numeric_values[n // 2]
                }
            else:
                value_counts = {}
                for v in values:
                    value_counts[str(v)] = value_counts.get(str(v), 0) + 1
                
                stats[col] = {
                    "type": "categorical",
                    "count": len(values),
                    "unique": len(value_counts),
                    "most_common": sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                }
        
        result = {"dataset_id": dataset_id, "statistics": stats}
        self.analysis_results.append(result)
        
        return {"success": True, "analysis": result, "message": f"Analyzed {len(stats)} columns"}
    
    async def create_chart(self, dataset_id: str, chart_type: str = "bar",
                          x_column: str = None, y_column: str = None) -> Dict:
        """Create an ASCII chart from data."""
        if dataset_id not in self.loaded_datasets:
            return {"success": False, "error": f"Dataset not found: {dataset_id}"}
        
        dataset = self.loaded_datasets[dataset_id]
        rows = dataset["rows"]
        
        if not x_column:
            x_column = dataset["headers"][0] if dataset["headers"] else None
        if not y_column:
            y_column = dataset["headers"][1] if len(dataset["headers"]) > 1 else None
        
        x_values = [row.get(x_column, "") for row in rows[:20]]
        y_values = []
        for row in rows[:20]:
            try:
                y_values.append(float(row.get(y_column, 0)))
            except (ValueError, TypeError):
                y_values.append(0)
        
        chart = self._generate_ascii_chart(x_values, y_values, chart_type)
        
        return {
            "success": True,
            "chart_type": chart_type,
            "ascii_chart": chart,
            "message": f"Generated {chart_type} chart"
        }
    
    def _generate_ascii_chart(self, x_values: List, y_values: List[float], chart_type: str) -> str:
        """Generate an ASCII chart."""
        if not y_values:
            return "No data to display"
        
        max_y = max(y_values)
        min_y = min(y_values)
        range_y = max_y - min_y if max_y != min_y else 1
        height = 10
        width = min(len(x_values), 50)
        chart_lines = []
        
        if chart_type == "bar":
            for i in range(height, -1, -1):
                threshold = min_y + (range_y * i / height)
                line = f"{threshold:>8.2f} |"
                for j in range(width):
                    if j < len(y_values) and y_values[j] >= threshold:
                        line += "##"
                    else:
                        line += "  "
                chart_lines.append(line)
            chart_lines.append(" " * 9 + "+" + "-" * (width * 2))
        
        return "\n".join(chart_lines)
    
    async def filter_data(self, dataset_id: str, condition: Dict) -> Dict:
        """Filter dataset based on conditions."""
        if dataset_id not in self.loaded_datasets:
            return {"success": False, "error": f"Dataset not found: {dataset_id}"}
        
        dataset = self.loaded_datasets[dataset_id]
        rows = dataset["rows"]
        
        filtered = []
        for row in rows:
            match = all(row.get(col) == value for col, value in condition.items())
            if match:
                filtered.append(row)
        
        return {"success": True, "original_count": len(rows), "filtered_count": len(filtered), "data": filtered[:100]}
    
    async def export_data(self, dataset_id: str, output_path: str, format: str = "csv") -> Dict:
        """Export dataset to file."""
        if dataset_id not in self.loaded_datasets:
            return {"success": False, "error": f"Dataset not found: {dataset_id}"}
        
        dataset = self.loaded_datasets[dataset_id]
        rows = dataset["rows"]
        headers = dataset["headers"]
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format == "csv":
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(rows)
            elif format == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(rows, f, indent=2)
            else:
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            return {"success": True, "path": str(output_file), "rows_exported": len(rows)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute(self, action: str, **kwargs) -> Dict:
        """Generic execute method."""
        actions = {
            "read_csv": lambda: self.read_csv(kwargs.get("path", ""), kwargs.get("delimiter", ","), kwargs.get("has_header", True)),
            "read_json": lambda: self.read_json(kwargs.get("path", "")),
            "read_excel": lambda: self.read_excel(kwargs.get("path", ""), kwargs.get("sheet")),
            "analyze_statistics": lambda: self.analyze_statistics(kwargs.get("dataset_id", ""), kwargs.get("columns")),
            "create_chart": lambda: self.create_chart(kwargs.get("dataset_id", ""), kwargs.get("chart_type", "bar"), kwargs.get("x_column"), kwargs.get("y_column")),
            "filter_data": lambda: self.filter_data(kwargs.get("dataset_id", ""), kwargs.get("condition", {})),
            "export_data": lambda: self.export_data(kwargs.get("dataset_id", ""), kwargs.get("output_path", "output.csv"), kwargs.get("format", "csv"))
        }
        
        if action in actions:
            return await actions[action]()
        return {"success": False, "error": f"Unknown action: {action}"}
