class _crayons:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    def __init__(self, text, _color=""):
        color = self.__getattribute__(_color.upper())
        self.data = color + text + self.ENDC

    def __repr__(self):
        return self.data


def crayons(text, color):
    return str(_crayons(text, color))


try:
    import requests

    USE_REQUESTS = True
except:
    print(crayons("[error]requests not installed", "FAIL"))
    print("Install latest version of requests by using")
    print(crayons("pip install requests", "BOLD"))
    quit()
    USE_REQUESTS = False
import re
import os
import threading
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

if not os.path.isdir(CACHE_DIR):
    print(crayons("No Cache Directory found", "warning"))
    os.mkdir(CACHE_DIR)


def fetch_(_url) -> None:
    url = _url.strip()
    res = compat_request(url).fetch()
    if res:
        print(crayons("[Failed]", "FAIL") + url)
    else:
        print(crayons("[Blocked]", "OKGREEN") + url)


def fire_requests():
    with open(HOSTS_FILE, "r") as f:
        for line in f:
            threads = threading.Thread(target=fetch_, args=(line,))
            threads.start()


def check_cached_hosts():
    print(crayons("Checking for cached host files in %s" % CACHE_DIR, "BOLD"))
    if not os.path.isfile(HOSTS_FILE) or os.path.getsize(HOSTS_FILE) <= 10000:
        print(crayons("No .hosts file found..fetching files", "warning"))
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
        http = _request.Request(url, headers=headers, method=method)
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
                r = _request.urlopen(func)
                self.data = {"headers": dict(r.info()), "body": r.read().decode()}
        except Exception as e:
            self.data = None

    def fetch(self):
        return self.data


if __name__ == "__main__":
    check_cached_hosts()
    fire_requests()
