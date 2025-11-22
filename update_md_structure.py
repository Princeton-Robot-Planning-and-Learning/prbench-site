import re
from pathlib import Path

def extract_variant_specific_info(description_text, group_description):
    """
    Extract only the variant-specific information from the description.
    This includes lines that mention specific numbers of objects/obstacles/blocks/passages.
    """
    variant_lines = []
    
    # Split into lines and process
    for line in description_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Skip lines that are already in the group description
        if line in group_description:
            continue
            
        # Look for variant-specific patterns - only lines that specify exact counts
        # These patterns look for "always X" followed by a noun (blocks, obstacles, passages, etc.)
        patterns = [
            r'always \d+\s+\w+\s+(blocks?|obstacles?|obstructions?|passages?|narrow passages?|obstacle blocks?|parts?|buttons?)',
        ]
        
        is_variant_specific = False
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                is_variant_specific = True
                break
        
        # Special case: "There are always X blocks/obstacles/etc"
        if re.match(r'^(In this environment,\s+)?[Tt]here are always \d+', line):
            is_variant_specific = True
            
        if is_variant_specific:
            # Clean up the line - remove leading "In this environment, "
            cleaned_line = re.sub(r'^In this environment,\s+', '', line, flags=re.IGNORECASE)
            # Capitalize first letter
            cleaned_line = cleaned_line[0].upper() + cleaned_line[1:] if cleaned_line else cleaned_line
            variant_lines.append(cleaned_line)
    
    if variant_lines:
        return '\n'.join(variant_lines)
    else:
        # Return a generic message if no specific variant info found
        return "This variant has a specific configuration. See the observation space below for details."

def update_markdown_structure(filepath):
    """
    Update markdown structure to:
    1. Put Environment Group Description first
    2. Replace Description with Variant Description (only variant-specific info)
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract header (title and GIF)
    header_match = re.match(r'(# .*?\n!\[.*?\].*?\n\n)', content, re.DOTALL)
    if not header_match:
        print(f"  ⚠ Could not find header pattern")
        return False
    
    header = header_match.group(1)
    
    # Extract Environment Group Description
    group_desc_match = re.search(r'### Environment Group Description\s*\n(.*?)(?=\n###|\Z)', content, re.DOTALL)
    if not group_desc_match:
        print(f"  ⚠ Could not find Environment Group Description")
        return False
    group_desc = group_desc_match.group(1).strip()
    
    # Check if Description section exists (old format)
    desc_match = re.search(r'### Description\s*\n(.*?)(?=\n###|\Z)', content, re.DOTALL)
    
    # Check if Variant Description already exists (new format)
    variant_desc_match = re.search(r'### Variant Description\s*\n(.*?)(?=\n###|\Z)', content, re.DOTALL)
    
    if desc_match:
        # Old format - extract variant info from Description
        desc_full = desc_match.group(1).strip()
        variant_desc = extract_variant_specific_info(desc_full, group_desc)
        needs_update = True
    elif variant_desc_match:
        # New format - check if order is correct
        # Find positions
        group_pos = content.find('### Environment Group Description')
        variant_pos = content.find('### Variant Description')
        
        if group_pos > variant_pos or group_pos < len(header):
            # Order is wrong or group desc is not right after header
            variant_desc = variant_desc_match.group(1).strip()
            needs_update = True
        else:
            # Already in correct format
            print(f"  ✓ Already in correct format")
            return False
    else:
        print(f"  ⚠ Could not find Description or Variant Description")
        return False
    
    # Extract everything from Initial State Distribution onwards
    rest_match = re.search(r'(### Initial State Distribution.*)', content, re.DOTALL)
    if not rest_match:
        print(f"  ⚠ Could not find Initial State Distribution")
        return False
    rest = rest_match.group(1)
    
    # Build new content in correct order
    new_content = header
    new_content += '### Environment Group Description\n'
    new_content += group_desc + '\n\n'
    new_content += '### Variant Description\n'
    new_content += variant_desc + '\n\n'
    new_content += rest
    
    # Write the updated content
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True

# Main execution
def main():
    md_dir = Path('markdowns')
    
    if not md_dir.exists():
        print(f"Error: {md_dir} directory not found")
        return
    
    md_files = sorted(md_dir.glob('*.md'))
    print(f"Found {len(md_files)} markdown files\n")
    
    updated = 0
    skipped = 0
    errors = 0
    
    for md_file in md_files:
        print(f"Processing: {md_file.name}")
        try:
            if update_markdown_structure(md_file):
                print(f"  ✓ Updated successfully")
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            errors += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Total: {len(md_files)}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
