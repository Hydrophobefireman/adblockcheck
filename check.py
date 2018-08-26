try:
    import requests

    USE_REQUESTS = True
except:
    import httplib2

    USE_REQUESTS = False
import re
import os
import threading
import itertools
import time

headers = {
    "Accept-Encoding": "gzip,deflate",
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 10.0; en-US) AppleWebKit/604.1.38 (KHTML, like Gecko) Chrome/68.0.3325.162",
    "Upgrade-Insecure-Requests": "1",
    "dnt": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
}
CACHE_DIR = ".cachedhosts"
HOSTS_FILE = os.path.join(CACHE_DIR, ".hosts")
IGNORE = [
    "127.0.0.1",
    "0.0.0.0",
    "255.255.255.255",
    "fe80::1%lo0",
    "ff00::0",
    "ff00::0",
    "ff02::1",
    "ff02::2",
    "ff02::3",
]
URL_REGEX = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"
HOSTS = [
    "https://hosts-file.net/download/HOSTS-Optimized.txt",
    "http://sbc.io/hosts/hosts",
    "https://zerodot1.gitlab.io/CoinBlockerLists/hosts",
    "https://raw.githubusercontent.com/jerryn70/GoodbyeAds/master/Hosts/GoodbyeAds.txt",
    "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0",
    "https://someonewhocares.org/hosts/hosts",
    "https://raw.githubusercontent.com/EnergizedProtection/block/master/spark/formats/hosts",
    "https://raw.githubusercontent.com/EnergizedProtection/block/master/bluGo/formats/hosts",
    "https://adaway.org/hosts.txt",
    "https://raw.githubusercontent.com/EnergizedProtection/block/master/blu/formats/hosts",
    "http://winhelp2002.mvps.org/hosts.txt",
]
ALT_HOST_SOURCES = []


def debug(s):
    print("[debug]%s" % (s))
    return


def info(s):
    print("[info]%s" % s)
    return


if not os.path.isdir(CACHE_DIR):
    info("No Cache Directory found")
    os.mkdir(CACHE_DIR)


def fetch_(_url) -> None:
    url = _url.strip()
    time.sleep(0.2)
    res = compat_request(url).fetch()
    if res:
        print("[Warning]Ad Blocker Failed for:%s" % url)
    else:
        print("Ad Blocked:", url)


def fire_requests():
    with open(HOSTS_FILE, "r") as f:
        for line in f:
            threads = threading.Thread(target=fetch_, args=(line,))
            threads.start()


def check_cached_hosts():
    debug("Checking for cached host files in %s" % CACHE_DIR)
    if not os.path.isfile(HOSTS_FILE) or os.path.getsize(HOSTS_FILE) <= 10000:
        info("No .hosts file found..fetching files")
        data = []
        for host in HOSTS:
            print(host)
            page = compat_request(host, method="get").fetch()
            print("WRITING")
            data += domains_only(page.get("body"))
        with open(HOSTS_FILE, "a") as f:
            print("writing to file:")
            f.write("\n".join(list(set(data))))


def domains_only(_host: str) -> list:
    host = "\n".join([s for s in _host.splitlines() if "#" not in s])
    """get domains from group of hosts file..and prepend http to it"""
    return list(
        set(
            [
                "http://" + s if not s.startswith("http") else s
                for s in [
                    a
                    for a in re.findall(URL_REGEX, host)
                    if not any(a == url for url in IGNORE)
                ]
            ]
        )
    )


def compat_request(url, method="head"):
    if not USE_REQUESTS:
        http = httplib2.Http()
    else:
        http = getattr(requests, method)
    return generate_request(http, USE_REQUESTS, url, headers, method)


class generate_request:
    def __init__(self, func, req, url, headers, method):
        try:
            if req:
                r = func(url, headers=headers)
                self.data = {"headers": r.headers, "body": r.text}
            else:
                r = func(url, headers=headers, method=method)
                self.data = {"headers": r[0], "body": r[1].decode()}
        except Exception as e:
            self.data = None

    def fetch(self):
        return self.data


if __name__ == "__main__":
    check_cached_hosts()
    fire_requests()
