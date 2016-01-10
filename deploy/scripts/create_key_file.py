#!python3
"""
dynamically creates a key file that is used for CSRF protection
"""
import os
import random

secret_key_file = "network_config_generator.key"

if not os.path.exists(secret_key_file):
    chars = "abcdefghijklmnopqrstuvwxyz" \
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
            "0123456789_-+"
    key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
    f = open(secret_key_file, "w")
    f.write(key)
    f.close()
