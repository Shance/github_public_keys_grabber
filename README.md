# GitHub public keys grabber
## Overview
This tool will iterate over all GitHub users and grab their public.
GitHub API allow authenticated users to do 5000 requests in hours. To get one user info this script hit API twice: first - to get user info and second - to get his public keys, so it can do 2500 users in hour.
For now there is around *17000000* users. Let's do a simple math:
17000000 / 2500 = 6800 hours of work. It's around 283 days, or 9 month of 24/7 seven computer work. Good luck!

## Requirements
- Python 2.7
- MySQL server

### Python dependencies
- Github3.py v1.0.a2
- pyMySQL

## Installation
To install Python dependencies run:
`pip install -r dependencies.txt`

Create MySQL database, for example, **github_keys** and create schema:
`mysql -u user -p github_keys < schema.sql`

## Configuration
Open **getkeys.py** and change MySQL configuration in function **db_connect()**:
Define MySQL user, password and database.
If your server use socket for connection, uncomment **unix_socket** line and define it's location, 
else define server address in **host** param.

Then, in the end of the file, define you GitHub user name and password.

Done!

## Usage
`python getkeys.py`

If you want to continue from, for example, 100 user, specify this ID in the first param like so
`python getkeys.py 100`

## Feedback
Please feel free to contact me about anything