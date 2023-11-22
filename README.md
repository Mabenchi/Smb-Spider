<br/>
<p align="center">
  <h3 align="center">Smb Spider</h3>

  <p align="center">
    <strong>"A lightweight tool to help you enumerate smb shares." </strong>
    <br/>
    <br/>
  </p>
</p>



## Table Of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
* [Usage](#usage)

## About The Project

This script will help you enumerate interesting files from a given share, by specifying extensions or filenames to look for, it will list or/and download them for you.

## Getting Started

1. Clone the repo

```sh
https://github.com/MarouaneBenchiekh/Smb-Spider
```

3. Install python modules

```sh
pip intall -r requirements.txt
```

4. Run the command

```JS
smbspider.py [-h] [-s SHARE] [-u username] [-p password] [-port [destination port]] [-l L] [-x extensions] [--download download] Target
```
## Usage
```
   _____           __       _____       _     __         
  / ___/____ ___  / /_     / ___/____  (_)___/ /__  _____
  \__ \/ __ `__ \/ __ \    \__ \/ __ \/ / __  / _ \/ ___/
 ___/ / / / / / / /_/ /   ___/ / /_/ / / /_/ /  __/ /    
/____/_/ /_/ /_/_.___/   /____/ .___/_/\__,_/\___/_/     
                             /_/                         

usage: smbspider.py [-h] [-s SHARE] [-u username] [-p password] [-port [destination port]] [-l L] [-x extensions] [--download download] Target

This script will help enumerate intresting files form a given share

positional arguments:
  Target                Server name/ip

options:
  -h, --help            show this help message and exit
  -s SHARE, --share SHARE
                        Name of the share to access. If not specified a list of existing shares will be listed.
  -u username           username of the account. Ex: 'domain/username'
  -p password           password of the account
  -port [destination port]
                        Destination port to connect to SMB Server
  -l L                  input file wordlist of filenames to look for in the smb share.
  -x extensions         exetension to look for in the smb share. Ex: '-x exe,txt,conf'
  --download download   Retrieve all found files to the given directory, if directory doesn't exist a it will be created. Ex: --download path/to/directory
```
