import sys
import argparse
from smb.SMBConnection import SMBConnection
from yaspin import yaspin
import pyfiglet
import socket
from nmb.NetBIOS import NetBIOS
from tabulate import tabulate
import os

# SMB server details
server_ip = ''
share_name = ''
domain = ''
file_list = []
file_paths = ['']

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


interesting_files = []
interesting_extensions = []

files_found = []
spinner = yaspin()
file_count = 0

def clear_line():
    sys.stdout.write("\033[2K")  # Clear the entire current line
    sys.stdout.write("\033[1G")  # Move the cursor to the beginning of the line
    sys.stdout.flush()

def get_netBiosName(ip_address):
    try:
        net = NetBIOS()
        net_name = str(net.queryIPForName(ip_address)).strip("['").strip("']")
        return net_name
    except socket.herror:
        return None

#Get files recursively from directories in share
def get_all_files(connection, path):
    global file_count
    file_list = connection.listPath(share_name, path)
    if path == '/':
        path = ''
    files = []
    for file in file_list:
        if file.filename not in (".", ".."):
            files.append([file.filename, file.isDirectory])
            if file.isDirectory:
                last_element = files[-1]
                last_element.append(get_all_files(conn, path + '/' + last_element[0]))
            else:
                file_count = file_count + 1
    return files

#Print in tree form
def print_file_tree(files, layer = 0):
    space = "   " * layer
    for file in files:
        if layer != 0:
            print(space + "|")
        else:
            print()
        print("{}- {}".format(space, file[0]))
        if file[1]:
            print_file_tree(file[2], layer + 1)

def print_file_path(files, path = ''):
    for file in files:
        if (path):
            print('/', end="")
            file_paths[-1] =  '/'
        print(path + '/', end="")
        if (file_paths[-1] == ''):
            file_paths[-1] =  path + '/'
        else:
            file_paths[-1] =  file_paths[-1] + path + '/'
        if (file[1]):
            if (len(file[2])):
                print_file_path(file[2], file[0])
            else:
                file_paths.pop()
                clear_line()
        else:
            # print('/' , end='')
            if (test_print_file(file[0])):
                file_paths[-1] = file_paths[-1] +  (file[0])
                file_paths.append('')

def test_print_file(file):
    if len(interesting_extensions) != 1:
        for suffix in interesting_extensions:
            if file.endswith(suffix):
                print(bcolors.FAIL + file + bcolors.ENDC)
                return True
    if len(interesting_files) != 1:
        for filename in interesting_files:
            if filename in file:
                print(bcolors.FAIL + file + bcolors.ENDC)
                return True
    if (len(interesting_files) == 0 and len(interesting_extensions) == 0):
        print(bcolors.FAIL + file + bcolors.ENDC)
        return True
    else:
        clear_line()
        return False

#List Share/Directory Files
def list_files():
    print(bcolors.OKGREEN + '[+] Checking //{}/{}'.format(server_ip, share_name)  + bcolors.ENDC)
    print()
    print('File Path')
    print("------------")
    global file_list
    file_list = get_all_files(conn, '/')
    #print_file_tree(file_list)
    global file_paths
    file_paths.append('')
    print_file_path(file_list)

def list_shares():
    print(bcolors.OKGREEN + '[+] Checking //{}'.format(server_ip)  + bcolors.ENDC)
    print()

    shares = conn.listShares()
    table_data = []
    for share in shares:
        share_name = share.name
        comments = share.comments
        readable = "Yes"
        writable = "Yes"

        # Check read access by listing the share directory
        try:
            conn.listPath(share.name, "/")
        except Exception as e:
            readable = "No"

        # Check write access by creating a test file
        test_file_path = f"{share.name}/test_file.txt"
        try:
            conn.createFile(share.name, test_file_path)
            conn.deleteFiles(share.name, test_file_path)
        except Exception as e:
            writable = "No"

        table_data.append([share_name, readable, writable, comments])

    table_headers = ["Share Name", "Read Access", "Write Access", "Description"]
    table = tabulate(table_data, headers=table_headers)
    print(table)

def download_files(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    for file_path in file_paths:
        sub_directory = ''
        destination_path = directory_path
        # Extract the file name from the file path
        if file_path.count('/') != 1:
            directories = file_path.split('/')
            directories.pop(0)
            directories.pop()
            for directory in directories:
                sub_directory += directory + '/'
                destination_path = os.path.join(directory_path, sub_directory)
                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)

        file_name = os.path.basename(file_path)
        # Construct the destination path by joining the destination directory and the file name
        final_destination_path = os.path.join(destination_path, file_name)
        with open(final_destination_path, 'wb') as file_obj:
                    # Retrieve the file from the SMB share
                    conn.retrieveFile(share_name, file_path, file_obj)

# Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='SMB Spider',
                    description='This script will help enumerate intresting files form a given share',)
    
    parser.add_argument('-u', default='', metavar='username', help="username of the account. Ex: 'domain/username'")
    parser.add_argument('-p', default='', metavar='password', help="password of the account")
    parser.add_argument('-port', choices=['139', '445'], nargs='?', default='445', metavar="destination port", help='Destination port to connect to SMB Server')
    # parser.add_argument('-k', metavar='kerberos login', help='Use Kerberos authentication. Grabs credentials from ccache file '
    #                                                    '(KRB5CCNAME) based on target parameters. If valid credentials '
    #                                                    'cannot be found, it will use the ones specified in the command '
    #                                                    'line')
    parser.add_argument('-l', type=argparse.FileType('r'), help='input file wordlist of filenames to look for in the smb share.')
    parser.add_argument('-x', default='', metavar='extensions', help="exetension to look for in the smb share. Ex: '-x exe,txt,conf'")
    parser.add_argument('--download', default='', metavar='download', help="Download all downloaded files ti the given directory. Ex: --download /tmp/")
    # parser.add_argument("-aesKey", metavar = "hex key",  help='AES key to use for Kerberos Authentication '
    #                                                                         '(128 or 256 bits)')
    parser.add_argument('target', metavar='Target', help="Server name/ip")
    parser.add_argument('-s','--share', help="Name of the share to access")
    #argcomplete.autocomplete(parser)

    print(pyfiglet.figlet_format("Smb Spider", font = "slant" ))

    args = parser.parse_args()

    if (args.p == '' and args.u != ''):
        from getpass import getpass
        args.p = getpass("Password:")

    if (args.u != ''):
        if ('/' in args.u):
            split = args.u.split('/')
            args.u = split[1]
            domain = split[0]
    if args.l is not None:
        for line in args.l:
            interesting_files.append(line.strip())
    if len(args.x) != 0:
        if ',' in args.x:
            interesting_extensions.extend(args.x.split(','))
        else:
            interesting_extensions.extend(['',args.x])
    server_name = get_netBiosName(args.target)
    # Create an SMB connection object
    conn = SMBConnection(args.u, args.p, 'smbspider', server_name, use_ntlm_v2=False, domain=domain)
    share_name = args.share
    server_ip = args.target
    # try:
    print(bcolors.WARNING + '[!] Trying Connection...' + bcolors.ENDC)
    # Connect to the SMB server
    conn.connect(args.target)
    # Check if the connection is successful

    if conn:
        # List files and directories in the shared folder
        if args.share is not None:
            list_files()
        else:
            list_shares()
        if args.download != '':
            file_paths.pop()
            download_files(args.download)
        conn.close()
    # except:
    #     print(bcolors.FAIL + '[-] Failed to connect to the SMB server!' + bcolors.ENDC, file=sys.stderr)