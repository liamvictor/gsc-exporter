import os
from collections import defaultdict
from urllib.parse import urlparse # Not directly used for parsing, but good for context on FQDNs

def get_available_sites():
    """
    Scans the 'output' directory and returns a dictionary of available sites,
    grouped by their base domain. Each site is listed with both potential
    command-line formats (sc-domain: for base, and https:// for all).
    """
    output_dir = 'output'
    if not os.path.isdir(output_dir):
        print(f"Error: Directory '{output_dir}' not found.")
        return None

    try:
        sites_grouped = defaultdict(set) # Use a set to avoid duplicates
        dir_names = [name for name in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, name))]

        for name in dir_names:
            # Heuristic to find the base domain
            # This logic tries to be robust for common TLDs like .co.uk
            parts = name.split('.')
            if len(parts) > 2 and parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'ac', 'ltd', 'info', 'biz', 'io']: # Added more common TLD parts
                base_domain = '.'.join(parts[-3:])
            elif len(parts) > 1:
                base_domain = '.'.join(parts[-2:])
            else:
                base_domain = name # For single-part names or unusual cases
            
            # Add the sc-domain property for the base domain
            sites_grouped[base_domain].add(f"sc-domain:{base_domain}")
            
            # Add the https:// URL-prefix property for the current directory name
            sites_grouped[base_domain].add(f"https://{name}")
        
        # Convert sets to lists for sorting
        return {k: list(v) for k, v in sites_grouped.items()}

    except OSError as e:
        print(f"Error reading directory '{output_dir}': {e}")
        return None

if __name__ == "__main__":
    sites_by_base = get_available_sites()
    if sites_by_base:
        print("Available sites for use in reports (choose the correct format based on your GSC property type):\n")
        
        # Sort base domains alphabetically
        for base_domain in sorted(sites_by_base.keys()):
            print(f"# {base_domain}")
            
            properties = sites_by_base[base_domain]
            
            def sort_key(prop_string):
                """Sorts properties by sc-domain, then www, then base domain, then alphabetically."""
                if prop_string == f"sc-domain:{base_domain}":
                    return (0, prop_string) # Domain property first
                if prop_string == f"https://www.{base_domain}":
                    return (1, prop_string) # www. version next
                if prop_string == f"https://{base_domain}":
                    return (2, prop_string) # Base domain as URL property
                
                # All other URL-prefix properties, sorted alphabetically
                return (3, prop_string)

            for prop in sorted(properties, key=sort_key):
                print(prop)
            print("") # Add a blank line for readability between groups
            
    else:
        print("No sites found in the 'output' directory.")
