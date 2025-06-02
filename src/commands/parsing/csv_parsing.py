import csv
import re
from typing import List, Dict, Optional, Union
import chardet
import io

class CommandParser:
    
    def __init__(self, vendor_name: str):
        self.vendor_name = vendor_name
        self.commands_data = []
        self.tags_data = []
        self.tag_hierarchy = {}
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
    
    def is_tag_row(self, row: List[str]) -> bool:
        """
        Check if a row represents a tag based on content in the first column
        and emptiness of subsequent columns (Command, Description, Example).
        """
        if not row: # Handle empty rows
            return False
        
        first_col_content = row[0].strip()
        
        # A tag row must have content in the first column.
        if not first_col_content:
            return False
            
        # A tag row should have empty content in the columns where
        # command, description, and example would typically be.
        # Check up to the 4th column (index 3) as per the CSV structure.

        # Check column 1 (index 1, where a command might be)
        if len(row) > 1 and row[1].strip():
            return False # Not a tag if the second column has content

        # Check column 2 (index 2, where a description might be)
        if len(row) > 2 and row[2].strip():
            return False # Not a tag if the third column has content

        # Check column 3 (index 3, where an example might be)
        if len(row) > 3 and row[3].strip():
            return False # Not a tag if the fourth column has content

        # If the first column has content and the next three are empty, it's a tag.
        return True
    #:
    
    def is_command_row(self, row: List[str]) -> bool:
        """Check if a row represents a command"""
        # Command rows have content in the COMMAND column (index 0 or 1)
        # and are not identified as tag rows
        if not row:
            return False
        
        command_text = self.clean_text(row[0])
        if not command_text and len(row) > 1:
            command_text = self.clean_text(row[1]) # Check second column if first is empty
            
        return bool(command_text and not self.is_tag_row(row))
    #:
    
    def extract_tag_info(self, tag_name: str) -> Dict[str, str]:
        """Extract tag information and determine parent relationship (placeholder)"""
        # This method is less critical now as parent logic is handled in parse_csv
        clean_name = self.clean_text(tag_name)
        return {'name': clean_name, 'parent': None} # Parent will be set during parsing
    #:
    
    def parse_csv(self, csv_content: str, main_tag_name_from_input: Optional[str] = None) -> Dict: 
        """
        Parse the CSV content (string) and extract structured data.
        All Tags found in the CSV will have 'main_tag_name_from_input' as their conceptual parent.
        """
        # current_tag will hold the *most recently found* tag name from the CSV
        current_tag = None 
        # fixed_main_parent_name will be the main_tag name provided by the user (from the form)
        fixed_main_parent_name = main_tag_name_from_input 
        
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
                if any(header.strip().lower() in ['command', 'description', 'example', 'tag', 'platform', 'version'] for header in row[:4]):
                    # If the first row is a header, skip it. If second row is header after warning, skip it.
                    if row_num == 1 or (row_num == 2 and 'WARNING!!' in csv_content):
                        continue 
                    continue # Skip if it looks like a header row later in file
                
                # Pad row to ensure it has enough elements for indexing
                while len(row) < 4:
                    row.append('')
                
                # Check if this is a tag row
                if self.is_tag_row(row):
                    tag_name_raw = row[0]
                    tag_name = self.clean_text(tag_name_raw)
                    
                    if tag_name:
                        # The 'current_tag' is always the one just found in the CSV
                        current_tag = tag_name 
                        
                        # All tags found in the CSV will have `fixed_main_parent_name` as their parent
                        tag_info = {
                            'name': current_tag,
                            'parent_name_from_input': fixed_main_parent_name, # Renamed for clarity
                            'vendor': self.vendor_name
                        }
                        
                        # Add to tags if not already present (checking name and parent_name_from_input)
                        if not any(c['name'] == tag_info['name'] and c['parent_name_from_input'] == tag_info['parent_name_from_input'] for c in self.tags_data):
                            self.tags_data.append(tag_info)
                
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
                            'tag': current_tag, # Assign the current active tag from CSV
                            'vendor': self.vendor_name,
                            'version': None  
                        }
                        
                        self.commands_data.append(command_info)
                        
        except Exception as e:
            print(f"Error parsing CSV: {e}")
        
        return {
            'vendor': self.vendor_name,
            'tags': self.tags_data,
            'commands': self.commands_data
        }
    #:

    def print_summary(self):
        """Print a summary of parsed data"""
        print(f"\n=== PARSING SUMMARY ===")
        print(f"Vendor: {self.vendor_name}")
        print(f"Tags found: {len(self.tags_data)}")
        print(f"Commands found: {len(self.commands_data)}")
        
        print(f"\n=== Tags ===")
        for cat in self.tags_data:
            parent_info = f" (parent: {cat['parent_name_from_input']})" if cat['parent_name_from_input'] else " (main tag)"
            print(f"- {cat['name']}{parent_info}")
        
        print(f"\n=== SAMPLE COMMANDS ===")
        for i, cmd in enumerate(self.commands_data[:10]):  # Show first 10
            print(f"{i+1}. Command: {cmd['command']}")
            print(f"   tag: {cmd['tag']}")
            print(f"   Description: {cmd['description'][:100]}..." if cmd['description'] and len(cmd['description']) > 100 else f"   Description: {cmd['description']}")
            print()
        #:

# Usage example (this function will now be called from the view)
def ParseCsv(vendor_name: str, main_tag_name_for_csv_context: Optional[str], csv_file_content: str) -> Dict:
    """
    Parses CSV content and returns structured data for Django model insertion.
    
    Args:
        vendor_name (str): The vendor name provided by the user.
        main_tag_name_for_csv_context (Optional[str]): The name of the main tag provided by the user.
                                                   Tags from CSV will be conceptually linked to this name.
        csv_file_content (str): The decoded content of the CSV file.

    Returns:
        Dict: A dictionary containing 'vendor', 'tags', and 'commands' data.
    """
    
    parser = CommandParser(vendor_name=vendor_name)
    # Pass the name string as the argument to the parser
    parsed_data = parser.parse_csv(csv_file_content, main_tag_name_from_input=main_tag_name_for_csv_context)
    
    return parsed_data
#: