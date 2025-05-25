import csv
import re
from typing import List, Dict, Optional, Union
import chardet
import io

class CommandParser:
    
    def __init__(self, vendor_name: str):
        self.vendor_name = vendor_name
        self.commands_data = []
        self.categories_data = []
        self.category_hierarchy = {}
    #:
        
    def detect_encoding(self, data: Union[bytes, str]) -> str:
        """Detect the encoding of the CSV data."""
        if isinstance(data, str): # If already a string, assume utf-8
            return 'utf-8'
        result = chardet.detect(data)
        return result['encoding'] or 'utf-8'
    #:
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove quotes if they wrap the entire string
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return text
    #:
    
    def is_category_row(self, row: List[str]) -> bool:
        """
        Check if a row represents a category based on content in the first column
        and emptiness of subsequent columns (Command, Description, Example).
        """
        if not row: # Handle empty rows
            return False
        
        first_col_content = row[0].strip()
        
        # A category row must have content in the first column.
        if not first_col_content:
            return False
            
        # A category row should have empty content in the columns where
        # command, description, and example would typically be.
        # Check up to the 4th column (index 3) as per the CSV structure.

        # Check column 1 (index 1, where a command might be)
        if len(row) > 1 and row[1].strip():
            return False # Not a category if the second column has content

        # Check column 2 (index 2, where a description might be)
        if len(row) > 2 and row[2].strip():
            return False # Not a category if the third column has content

        # Check column 3 (index 3, where an example might be)
        if len(row) > 3 and row[3].strip():
            return False # Not a category if the fourth column has content

        # If the first column has content and the next three are empty, it's a category.
        return True
    #:
    
    def is_command_row(self, row: List[str]) -> bool:
        """Check if a row represents a command"""
        # Command rows have content in the COMMAND column (index 0 or 1)
        # and are not identified as category rows
        if not row:
            return False
        
        command_text = self.clean_text(row[0])
        if not command_text and len(row) > 1:
            command_text = self.clean_text(row[1]) # Check second column if first is empty
            
        return bool(command_text and not self.is_category_row(row))
    #:
    
    def extract_category_info(self, category_name: str) -> Dict[str, str]:
        """Extract category information and determine parent relationship (placeholder)"""
        # This method is less critical now as parent logic is handled in parse_csv
        clean_name = self.clean_text(category_name)
        return {'name': clean_name, 'parent': None} # Parent will be set during parsing
    #:
    
    def parse_csv(self, csv_content: str, main_category: Optional[str] = None) -> Dict: 
        """
        Parse the CSV content (string) and extract structured data.
        All categories found in the CSV will have 'main_category' as their parent.
        """
        # We assume csv_content is already decoded to utf-8 string
        # encoding = self.detect_encoding(csv_content.encode('utf-8')) # Not needed if content is string
        
        # current_category will hold the *most recently found* category from the CSV
        current_category = None 
        # fixed_main_parent will be the fixed main_category provided by the user
        fixed_main_parent = main_category 
        
        try:
            # Use io.StringIO to treat the string content as a file
            csv_file = io.StringIO(csv_content)
            csv_reader = csv.reader(csv_file)
            
            for row_num, row in enumerate(csv_reader, 1):
                # Skip empty rows
                if not row or all(not cell.strip() for cell in row):
                    continue
                    
                # Skip the warning row and header row if they appear at the beginning
                if row_num == 1 and 'WARNING!!' in str(row):
                    continue
                # More robust header check
                if any(header.strip().lower() in ['command', 'description', 'example', 'category', 'os', 'version'] for header in row[:4]):
                    # If the first row is a header, skip it. If second row is header after warning, skip it.
                    if row_num == 1 or (row_num == 2 and 'WARNING!!' in csv_content): # Simplified check for warning presence
                        continue 
                    continue # Skip if it looks like a header row later in file
                
                # Pad row to ensure it has enough elements for indexing
                while len(row) < 4:
                    row.append('')
                
                # Check if this is a category row
                if self.is_category_row(row):
                    category_name_raw = row[0]
                    category_name = self.clean_text(category_name_raw)
                    
                    if category_name:
                        # The 'current_category' is always the one just found in the CSV
                        current_category = category_name 
                        
                        # All categories found in the CSV will have `fixed_main_parent` as their parent
                        category_info = {
                            'name': current_category,
                            'parent': fixed_main_parent, # Fixed parent from user input
                            'vendor': self.vendor_name
                        }
                        
                        # Add to categories if not already present (checking name and parent)
                        if not any(c['name'] == category_info['name'] and c['parent'] == category_info['parent'] for c in self.categories_data):
                            self.categories_data.append(category_info)
                
                # Check if this is a command row
                elif self.is_command_row(row):
                    command = self.clean_text(row[0]) or self.clean_text(row[1])
                    description = self.clean_text(row[2])
                    example = self.clean_text(row[3])
                    
                    if command:
                        command_info = {
                            'command': command,
                            'description': description if description else None,
                            'example': example if example else None,
                            'category': current_category, # Assign the current active category from CSV
                            'vendor': self.vendor_name,
                            'version': None  
                        }
                        
                        self.commands_data.append(command_info)
                        
        except Exception as e:
            print(f"Error parsing CSV: {e}")
        
        return {
            'vendor': self.vendor_name,
            'categories': self.categories_data,
            'commands': self.commands_data
        }
    
    # Removed export_to_json as it's not needed if we return the dict directly
    # def export_to_json(self, data: Dict) -> str:
    #     """
    #     Exports the parsed data (vendor, categories, commands) to a JSON string.
    #     """
    #     return json.dumps(data, indent=4, ensure_ascii=False)
    #:

    def print_summary(self):
        """Print a summary of parsed data"""
        print(f"\n=== PARSING SUMMARY ===")
        print(f"Vendor: {self.vendor_name}")
        print(f"Categories found: {len(self.categories_data)}")
        print(f"Commands found: {len(self.commands_data)}")
        
        print(f"\n=== CATEGORIES ===")
        for cat in self.categories_data:
            parent_info = f" (parent: {cat['parent']})" if cat['parent'] else " (main category)"
            print(f"- {cat['name']}{parent_info}")
        
        print(f"\n=== SAMPLE COMMANDS ===")
        for i, cmd in enumerate(self.commands_data[:10]):  # Show first 10
            print(f"{i+1}. Command: {cmd['command']}")
            print(f"   Category: {cmd['category']}")
            print(f"   Description: {cmd['description'][:100]}..." if cmd['description'] and len(cmd['description']) > 100 else f"   Description: {cmd['description']}")
            print()
        #:

# Usage example (this function will now be called from the view)
def ParseCsv(vendor_name: str, main_category: Optional[str], csv_file_content: str) -> Dict:
    """
    Parses CSV content and returns structured data for Django model insertion.
    
    Args:
        vendor_name (str): The vendor name provided by the user.
        main_category (Optional[str]): The main category provided by the user.
        csv_file_content (str): The decoded content of the CSV file.

    Returns:
        Dict: A dictionary containing 'vendor', 'categories', and 'commands' data.
    """
    
    parser = CommandParser(vendor_name=vendor_name)
    parsed_data = parser.parse_csv(csv_file_content, main_category=main_category)
    
    return parsed_data
#: