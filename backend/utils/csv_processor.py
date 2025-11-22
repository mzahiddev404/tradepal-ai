"""
CSV Processor for ingesting structured data (like Options Flow) into RAG.
"""
import pandas as pd
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class CSVProcessor:
    """Processor for CSV files to be used in RAG."""
    
    def process_csv(self, csv_path: str) -> List[Dict]:
        """
        Process a CSV file and return chunks of text.
        Each row is converted into a narrative sentence for better embedding.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            List of dictionaries with 'text' and 'metadata' keys
        """
        chunks = []
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            
            # Clean data: drop completely empty rows
            df.dropna(how='all', inplace=True)
            
            # Fill NaNs with empty string for text conversion
            df.fillna('', inplace=True)
            
            # Identify likely columns for options flow
            columns = [c.lower() for c in df.columns]
            
            # Process each row
            for idx, row in df.iterrows():
                # Create a narrative text chunk from the row
                # We try to be smart about formatting common financial columns
                
                text_parts = []
                
                # Date/Time
                date_col = next((c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()), None)
                if date_col and row[date_col]:
                    text_parts.append(f"On {row[date_col]}")
                
                # Ticker
                ticker_col = next((c for c in df.columns if 'symbol' in c.lower() or 'ticker' in c.lower()), None)
                if ticker_col and row[ticker_col]:
                    text_parts.append(f"ticker {row[ticker_col]}")
                
                # Sentiment/Type
                type_col = next((c for c in df.columns if 'type' in c.lower() or 'side' in c.lower() or 'sentiment' in c.lower()), None)
                if type_col and row[type_col]:
                    text_parts.append(f"showed {row[type_col]} activity")
                
                # Details (Premium, Strike, etc.)
                details = []
                for col in df.columns:
                    # Skip columns we already used or if value is empty
                    if col in [date_col, ticker_col, type_col] or not row[col]:
                        continue
                        
                    val = row[col]
                    # Format currency if it looks like a number and column has currency keywords
                    if isinstance(val, (int, float)) and any(k in col.lower() for k in ['premium', 'cost', 'value', 'price']):
                        details.append(f"{col}: ${val:,.2f}")
                    else:
                        details.append(f"{col}: {val}")
                
                if details:
                    text_parts.append("with details: " + ", ".join(details))
                
                # Construct final text
                # Fallback if we couldn't find specific columns: just dump the row
                if len(text_parts) < 2: 
                    text_content = ", ".join([f"{k}: {v}" for k, v in row.items() if v])
                else:
                    text_content = ", ".join(text_parts) + "."
                
                # Metadata
                metadata = {
                    "source": "csv",
                    "row": idx + 1,
                    "page": 1, # CSVs count as 1 "page" usually
                }
                
                # Add ticker to metadata if found (helps with search filtering)
                if ticker_col and row[ticker_col]:
                    metadata["ticker"] = str(row[ticker_col]).upper()
                
                chunks.append({
                    "text": text_content,
                    "metadata": metadata
                })
                
            logger.info(f"Processed CSV {csv_path}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing CSV {csv_path}: {e}")
            return []

# Global instance
csv_processor = CSVProcessor()

