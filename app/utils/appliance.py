"""
utility function for the appliance
"""
import subprocess

import re
import redis
import netifaces as ni


def verify_appliance_status():
    """
    simple verification method for the services on the appliance
    :return:
    """
    result = {
        "ftp": False,
        "tftp": False,
        "redis": False,
        "celery_worker": False
    }

    # assume that the setup script was running on the server, if the ports are open, TFTP and FTP should be available
    output = subprocess.check_output(["netstat", "-l"]).decode("utf-8")
    if "*:tftp" in output:
        result["tftp"] = True

    if "*:ftp" in output:
        result["ftp"] = True

    # we assume that the redis server is running locally, therefore we can use the CLI to test the connection
    rs = redis.Redis("localhost")
    try:
        if rs.ping():
            result["redis"] = True

    except:
        # ignore silently
        result["redis"] = False

    # to verify the state of the celery worker threads, we look at the processes
    output = subprocess.check_output(["ps", "ax"]).decode("utf-8")
    if ("celery" in output) and ("-A app.celery" in output):
        result["celery_worker"] = True

    return result


def is_valid_ipv4_address(text):
    """
    check if the given text is a valid IPv4 address
    :param text:
    :return:
    """
    ipv4_regex = '(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4]' \
                 '[0-9]|25[0-5])'

    if re.match(ipv4_regex, text) is None:
        return False
    return True


def get_local_ip_addresses():
    """
    returns a dictionary that contains the interface names and the associated IPv4 addresses
    :return:
    """
    result = {}
    intf_dict = ni.interfaces()
    for i in intf_dict:
        a = ni.ifaddresses(i)
        result[i] = list()
        for key in a.keys():
            for entry in a[key]:
                try:
                    if is_valid_ipv4_address(entry["addr"]) and (entry["addr"] not in "127.0.0.1"):
                        result[i].append(entry["addr"])

                except:
                    # silent ignore
                    pass
        if len(result[i]) == 0:
            del result[i]

    return result
