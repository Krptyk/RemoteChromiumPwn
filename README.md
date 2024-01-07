# RemoteChromiumPwn
A streamlined script for Chromium-based browsers that enables remote debugging, allowing users to extract, load, and manage cookie data as well as page information via a specified port, with output customization in human-readable or JSON format.

## View a detailed blog walkthrough of differnt use cases:
### <a href="https://krptyk.com/2023/11/12/remotechromiumpwn/">Chromium Remote Debugging: A Tactical Guide for Red Team Operations</a>


## Features

- **Dump Cookies**: Extract cookies from a remote debugging session and output them to the terminal or a file.
- **Load Cookies**: Load a list of cookies from a json file into a remote browser session.
- **Dump Pages**: Retrieve information about open pages and output it to the terminal or a file.
- **Flexible Output**: Choose between a human-readable format or JSON for output.
- **Customisable Port**: Connect to any specified remote debugging port.

## Installation

To use RemoteChromiumPwn, you'll need Python 3.x and the following Python packages:
- `requests`
- `websocket-client`
- `argparse`
- `json`

Install the required packages using pip:

    pip install requests websocket-client argparse json

## Usage

To get started with RemoteChromiumPwn, you can use the following command line arguments:

    python RemoteChromiumPwn.py --port <PORT> [options]

Here are the available options:

    --dump-cookies or -dc: Dump the cookies to the terminal or output file.
    --load-cookies or -lc: Load cookies from the specified input file.
    --dump-pages or -dp: Dump the pages information to the terminal or output file.
    --output or -o: Specify the output file to save the cookies or pages information.
    --format or -f: Choose the output format (standard or json). Defaults to standard.

## Examples

Dump cookies in human-readable format to the terminal:

    python RemoteChromiumPwn.py --port 9222 --dump-cookies

Load cookies from a file:

    python RemoteChromiumPwn.py --port 9222 --load-cookies path/to/cookies.json

Dump page information to a file in JSON format:

    python RemoteChromiumPwn.py --port 9222 --dump-pages --output pages_info.json --format json

##To Do:
Add the ability to load pages from .json file into the browser

## Contributing

Contributions to RemoteChromiumPwn are welcome! Feel free to fork the repository, make changes, and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.
