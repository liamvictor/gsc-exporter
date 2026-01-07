import os
import sys
import subprocess
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth import exceptions

# --- Configuration (copied from other scripts) ---
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

def get_gsc_service():
    """Authenticates and returns a Google Search Console service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Could not load credentials from {TOKEN_FILE}. Error: {e}")
            print("Will attempt to re-authenticate.")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Credentials have expired. Attempting to refresh...")
                creds.refresh(Request())
            except exceptions.RefreshError as e:
                print(f"Error refreshing token: {e}")
                print("The refresh token is expired or revoked. Deleting it and re-authenticating.")
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                creds = None
        
        if not creds:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(f"Error: {CLIENT_SECRET_FILE} not found. Please follow setup instructions in README.md.")
                return None
            
            print("A browser window will open for you to authorize access.")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print("Authentication successful. Credentials saved.")

    return build('webmasters', 'v3', credentials=creds)

def get_all_sites(service):
    """Fetches a list of all sites (properties) from the GSC account."""
    try:
        site_list = service.sites().list().execute()
        if 'siteEntry' in site_list:
            # Sort the sites alphabetically for predictable order
            sites = sorted([site['siteUrl'] for site in site_list['siteEntry']])
            return sites
        else:
            print("No sites found in your Google Search Console account.")
            return []
    except Exception as e:
        print(f"An error occurred while fetching the site list: {e}")
        return []

def main():
    """
    Runs the generate_gsc_wrapped.py script for every property in the GSC account.
    Passes any command-line arguments to the underlying script.
    """
    # Get any extra arguments passed to this script to forward them
    extra_args = sys.argv[1:]
    
    print("Authenticating with Google to get the list of all properties...")
    service = get_gsc_service()
    if not service:
        return

    print("\nFetching list of properties...")
    sites = get_all_sites(service)
    
    if not sites:
        return
        
    print(f"\nFound {len(sites)} properties. Preparing to run the Wrapped report for each.")
    print("The following properties will be processed:")
    for site in sites:
        print(f" - {site}")
    
    for site in sites:
        print(f"\n{'='*20} Running for: {site} {'='*20}")
        command = ['py', 'generate_gsc_wrapped.py', site] + extra_args
        
        print(f"Executing command: {' '.join(command)}")
        
        try:
            # We use subprocess.PIPE to capture output and print it in real-time
            # This provides a better user experience than waiting for the whole process to finish
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as process:
                for line in process.stdout:
                    print(line, end='')
            
            if process.returncode == 0:
                print(f"\n----- Successfully completed for {site} ----- ")
            else:
                 print(f"\n----- Script finished with return code {process.returncode} for {site} ----- ")

        except FileNotFoundError:
            print("\nError: 'py' command not found. Is Python installed and configured in your system's PATH?")
            print("You might need to use 'python' instead of 'py'.")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred while running the script for {site}: {e}")

if __name__ == '__main__':
    main()
