import os
from collections import defaultdict

def get_available_domains():
    """
    Scans the 'output' directory and returns a list of available domains,
    formatted and grouped for command-line use.
    """
    output_dir = 'output'
    if not os.path.isdir(output_dir):
        print(f"Error: Directory '{output_dir}' not found.")
        return None

    try:
        # Group domains by base domain
        domains_grouped = defaultdict(list)
        for name in os.listdir(output_dir):
            if os.path.isdir(os.path.join(output_dir, name)):
                # Heuristic to find the base domain (e.g., 'croneri.co.uk' from 'www.croneri.co.uk')
                parts = name.split('.')
                if len(parts) > 2 and parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'ac']:
                    base_domain = '.'.join(parts[-3:])
                elif len(parts) > 1:
                    base_domain = '.'.join(parts[-2:])
                else:
                    base_domain = name
                
                domains_grouped[base_domain].append(name)
        
        return domains_grouped

    except OSError as e:
        print(f"Error reading directory '{output_dir}': {e}")
        return None

if __name__ == "__main__":
    domains_by_base = get_available_domains()
    if domains_by_base:
        print("Available domains for use in reports:\n")
        
        # Sort base domains alphabetically
        for base_domain in sorted(domains_by_base.keys()):
            print(f"# {base_domain}")
            
            # Sort properties within the group: www first, then alphabetically
            properties = domains_by_base[base_domain]
            
            def sort_key(domain_name):
                # Primary sort key: 0 for www, 1 for others
                # Secondary sort key: the domain name itself for alphabetical sorting
                is_www = domain_name.startswith('www.')
                return (0 if is_www else 1, domain_name)

            for domain in sorted(properties, key=sort_key):
                print(f"sc-domain:{domain}")
            print("") # Add a blank line for readability between groups
            
    else:
        print("No domains found.")
