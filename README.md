# GitHub public keys grabber
This tool will iterate over all GitHub users and grab their public

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

### Configuration
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