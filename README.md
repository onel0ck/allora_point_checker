# Allora Points Checker

This project allows you to check the points of multiple Allora and EVM addresses on the Allora network.

**Disclaimer:** This project is for educational purposes only. Use it responsibly and in accordance with Allora's terms of service.

Follow me on Twitter: [@1l0ck](https://x.com/1l0ck)

## Features

- Asynchronous processing for efficient checking of multiple addresses
- Support for both Allora and EVM addresses
- Concurrent request handling with rate limiting
- Detailed logging with color-coded output
- Results saved to a log file with timestamp

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/onel0ck/allora_points_checker.git
   cd allora-points-checker
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Prepare the data file:
   - `wallets.txt`: Contains Allora and EVM addresses to check, one per line
   - `proxies.txt`: http://login:password@ip:port, one per line

## Usage

Run the script:
```
python main.py
```

## Results

- Results will be saved in a log file named `result_HHMM-DD-MM-YY.log`
- Console output will show real-time progress and final results

## Configuration

You can modify the following parameters in the `config.py` file:
- `CONCURRENT_TASKS`: Maximum number of concurrent tasks
- `THREAD_POOL_SIZE`: Size of the thread pool
- `URL_POST` and `URL_GET`: API endpoints
- `HEADERS_POST` and `HEADERS_GET`: Request headers

## Files Description

- `main.py`: The main script that orchestrates the checking process
- `config.py`: Contains configuration variables
- `utils.py`: Utility functions for reading wallets and handling requests
- `requirements.txt`: List of Python package dependencies
