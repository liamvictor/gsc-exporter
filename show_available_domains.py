import os

def get_available_domains():
    """
    Scans the 'output' directory and returns a list of available domains.
    Domains are identified by the names of the subdirectories.
    """
    output_dir = 'output'
    if not os.path.isdir(output_dir):
        print(f"Error: Directory '{output_dir}' not found.")
        return []

    try:
        domains = [name for name in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, name))]
        return domains
    except OSError as e:
        print(f"Error reading directory '{output_dir}': {e}")
        return []

if __name__ == "__main__":
    available_domains = get_available_domains()
    if available_domains:
        print("Available domains:")
        for domain in sorted(available_domains):
            print(f"- {domain}")
    else:
        print("No domains found.")
