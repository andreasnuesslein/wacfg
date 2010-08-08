import subprocess
import sys

from .output import OUT

def uniq(seq):
    seen = set()
    return [x for x in seq if x not in seen and not seen.add(x)]


def identify_server():
    servers = { # program-name, username
            "apache": "apache",
            "nginx": "nginx",
            "lighttpd": "lighttpd",
            }
    users = []
    for server,user in servers.items():
        args = ["/usr/bin/which", server]
        if not subprocess.call(args,stdout=subprocess.PIPE, stderr=subprocess.PIPE):
            users += [user]
    if not len(users):
        OUT.error("No webserver found on your system")
        sys.exit(1)
    if len(users) > 1:
        OUT.warn("More than one webserver found on your system. Using %s as user" % users[0])
    return users[0]

