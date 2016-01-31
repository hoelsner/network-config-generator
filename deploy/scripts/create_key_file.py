#!python3
"""
dynamically creates a key file (primary for the CSRF protection)
Usage:
    create_key_file.py
        generate a key for the CSRF protection (50 characters) and store it to the network_config_generator.key file

    create_key_file.py <filename> <length>
        generate a custom keyfile with a specific length

"""
import os
import sys
import random

# if less than two arguments are found, use default settings and generate the network_config_generator.key file
if len(sys.argv) < 2+1:
    secret_key_file = "network_config_generator.key"
    length = 50
else:
    secret_key_file = sys.argv[1]
    length = int(sys.argv[2])

# create the keyfile only if the file doesn't already exist
if not os.path.exists(secret_key_file):
    chars = "abcdefghijklmnopqrstuvwxyz" \
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
            "0123456789_-+"
    key = ''.join(random.SystemRandom().choice(chars) for _ in range(length))
    f = open(secret_key_file, "w")
    f.write(key)
    f.close()
