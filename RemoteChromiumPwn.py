import argparse
import requests
import websocket
import json
from collections import defaultdict

# Set up the command line argument parser
parser = argparse.ArgumentParser(description='Interact with the Chromium debug port to manage cookies and pages.')
parser.add_argument('--port', '-p', type=int, required=True, help='The debug port that Chromium is listening on.')
parser.add_argument('--dump-cookies', '-dc', action='store_true', help='If set, dump the cookies to terminal or output file.')
parser.add_argument('--load-cookies', '-lc', type=str, help='Input file to load cookies from. If set, cookies will be loaded from this file.')
parser.add_argument('--dump-pages', '-dp', action='store_true', help='If set, dump the pages information to terminal or output file.')
parser.add_argument('--output', '-o', type=str, help='Output file to save the cookies or pages information.')
parser.add_argument('--format', '-f', type=str, choices=['human', 'json'], default='human', help='Output format. Can be "human" or "json". Defaults to "human".')

# Parse the command line arguments
args = parser.parse_args()

def fetch_pages(port):
    try:
        response = requests.get(f'http://localhost:{port}/json')
        response.raise_for_status()  # Raise an HTTPError on bad response
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[+] Failed to fetch pages: {e}")
        return None

def dump_cookies(websocket_url, output_file=None, output_format='human'):
    try:
        print("[+] Connecting to the WebSocket and sending the command...")
        ws = websocket.WebSocket()
        ws.connect(websocket_url, suppress_origin=True)
        ws.send('{"id": 1, "method": "Network.getAllCookies"}')

        print("[+] Receiving and parsing the response...")
        response = ws.recv()

        # If output format is json or an output file is specified, work with raw response
        if output_format == 'json' or output_file:
            cookies_data = response if output_format == 'json' else json.dumps(json.loads(response), indent=4)

            if output_file:
                with open(output_file, 'w') as file:
                    file.write(cookies_data)
                    print(f"[+] Cookies have been written to {output_file} in {output_format} format.")
            else:
                print(cookies_data)

        # If output format is human and no file is specified, print human-readable format to terminal
        elif output_format == 'human' and not output_file:
            response_json = json.loads(response)
            cookies = response_json.get('result', {}).get('cookies', [])

            print("[+] Grouping cookies by domain...")
            cookies_by_domain = defaultdict(list)
            for cookie in cookies:
                cookies_by_domain[cookie['domain']].append(cookie)

            for domain, domain_cookies in cookies_by_domain.items():
                print(f"[+] Domain: {domain}")
                for cookie in domain_cookies:
                    print(f"  [+] Name: {cookie['name']}")
                    print(f"  [+] Value: {cookie['value']}")
                    print(f"  [+] Path: {cookie['path']}")
                    print(f"  [+] Expires: {cookie['expires']}")
                print('[+]' + '=' * 40)  # Add a separator line
    except websocket.WebSocketException as e:
        print(f"[+] WebSocket error: {e}")
    except json.JSONDecodeError as e:
        print(f"[+] JSON parsing error: {e}")
    except IOError as e:
        print(f"[+] File I/O error: {e}")

def load_cookies_from_file(file_path, websocket_url):
    ws = None
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # The cookies are under the 'result' key, and then 'cookies'.
            cookies_list = data.get('result', {}).get('cookies', [])

            # Check if cookies_list is actually a list
            if not isinstance(cookies_list, list):
                raise ValueError("The cookies file does not contain a list.")
            
        ws = websocket.WebSocket()  # Now this line only overwrites `ws` if it succeeds
        ws.connect(websocket_url, suppress_origin=True)
        
        for cookie in cookies_list:
            if not all(key in cookie for key in ["name", "value", "domain", "path"]):
                raise ValueError("One or more cookies are missing required fields.")
            
            ws.send(json.dumps({
                "id": 1,
                "method": "Network.setCookie",
                "params": cookie
            }))
            response = json.loads(ws.recv())
            
            if not response.get('result', {}).get('success', False):
                print(f"[-] Failed to set cookie: {cookie['name']}")
            else:
                print(f"[+] Cookie set successfully: {cookie['name']}")
        
        print(f"[+] Cookies loaded successfully from {file_path}.")
    except (IOError, ValueError, json.JSONDecodeError, websocket.WebSocketException) as e:
        print(f"[-] Error loading cookies: {e}")
    finally:
        if ws is not None:  # Only attempt to close `ws` if it was successfully created
            ws.close()

def dump_pages(port, output_file=None, output_format='human'):
    pages = fetch_pages(port)
    if pages:
        if output_format == 'json' or output_file:
            # Output as JSON if requested or if an output file is specified
            pages_info = json.dumps(pages, indent=4)
            if output_file:
                with open(output_file, 'w') as file:
                    file.write(pages_info)
                print(f"[+] Pages information has been written to {output_file} in JSON format.")
            else:
                print(pages_info)
        else:
            # Output in human-readable format
            for page in pages:
                print(f"Page ID: {page.get('id', 'N/A')}")
                print(f"Title: {page.get('title', 'N/A')}")
                print(f"URL: {page.get('url', 'N/A')}")
                print(f"WebSocket Debugger URL: {page.get('webSocketDebuggerUrl', 'N/A')}")
                print('-' * 40)  # Separator between pages

    else:
        print("[+] No pages found or failed to fetch page data.")

# Main execution logic
if args.dump_cookies:
    pages = fetch_pages(args.port)
    if pages:
        websocket_url = pages[0].get('webSocketDebuggerUrl')
        if websocket_url:
            dump_cookies(websocket_url, args.output, args.format)

if args.load_cookies:
    pages = fetch_pages(args.port)
    if pages:
        websocket_url = pages[0].get('webSocketDebuggerUrl')
        if websocket_url:
            load_cookies_from_file(args.load_cookies, websocket_url)


if args.dump_pages:
    dump_pages(args.port, args.output, args.format)
