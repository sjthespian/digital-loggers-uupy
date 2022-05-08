#!/usr/bin/env python3
#
# Port of Digital Logger UU to python for use with Home Assistant
# https://www.digital-loggers.com/cex.html
#

import sys
import re
import requests

norefresh = 0
# Change to
# norefresh=1
# to enable status caching

version = "4.5-py (c) DLI 2016"
type = "lpc"
prompt = "UU> "
response = None  # Global for response from requests

print(f"UserUtil {version}\n", file=sys.stderr)


def usage(msg=None):
    if msg:
        print(msg, file=sys.stderr)
    print(
        "Usage: UU <Host>[:port] <login:password> <[n]{on|off|pulse|status|power|name}|runNNN|interact> ...",
        file=sys.stderr,
    )
    sys.exit(1)


def RelLink(args):
    global response

    try:
        response = requests.get(f"{base}{args}")
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ) as e:
        print(f"ERROR: connecting to {epc} {str(e)}")
        sys.exit(1)
    if not response:
        if response.status_code != 404 or type == epc:
            print(response.content.decode("utf-8"), file=sys.stderr)
            sys.exit(1)
        return 0

    redirect_re = re.compile("<meta[^>]*?url=(.*?)[\"']", re.IGNORECASE)
    m = redirect_re.search(response.content.decode("utf-8"))
    if m:
        response = requests.get(f"{base}{m.group(1).strip('/')}")
        if not response:
            if response.status_code != 404 or type == epc:
                print(response.content.decode("utf-8"), file=sys.stderr)
                sys.exit(1)
            return 0


def cmd(arg=None):
    global response
    global type

    arg = arg.lower()
    arg = re.sub("(^[^1-8])", r"a\1", arg)

    m = re.search("^([1-8a])on$", arg)
    if m:
        if type == "lpc":
            RelLink(f"outlet?{m.group(1)}=ON")
        else:
            RelLink(f"outleton?{m.group(1)}")
        return True

    m = re.search("^([1-8a])off$", arg)
    if m:
        if type == "lpc":
            RelLink(f"outlet?{m.group(1)}=OFF")
        else:
            RelLink(f"outletoff?{m.group(1)}")
        return True

    m = re.search("^([1-8a])pulse$", arg)
    if m:
        if type == "lpc":
            RelLink(f"outlet?{m.group(1)}=CCL")
        else:
            RelLink(f"outletgl?{m.group(1)}")
        return True

    m = re.search("^([1-8a])status$", arg)
    if m:
        n = m.group(1)
        if n != "a":
            n = int(n)
        if norefresh and response:
            m = re.search(
                "<td.*?>([1-8])<\/td>.*?<\/td>[^\/]*?\W(ON|OFF)\W",
                response.content.decode("utf-8"),
                flags=re.MULTILINE | re.IGNORECASE,
            )
            if not m:
                ReLink("")
        else:
            RelLink("")

        content = response.content.decode("utf-8")

        if type == "lpc" and "<a href=outleto" in content:
            type = "epc"

        # newer firmware is easier to parse
        m = re.search(
            "<!-- state=([0-9a-f][0-9a-f]) lock=([0-9a-f][0-9a-f])",
            content,
        )
        if m:
            state = int(m.group(1), 16)
            lock = int(m.group(2), 16)
            for i in range(1, 9):
                if i == n or n == "a":
                    print(i, end="")
                    print(" ON" if state & (1 << (i - 1)) else " OFF", end="")
                    print(" LOCKED" if lock & (1 << (i - 1)) else "")
        else:
            for m in re.findall(
                "<td.*?>([1-8])<\/td>\s*<td>(.*?)<\/td>[^\/]*?\W(ON|OFF)\W",
                flags=re.IGNORECASE | re.MULTILINE,
            ):
                if m[0] == n or n == "a":
                    if m[2] == "ON":
                        print(f"{m[0]} ON")
                    else:
                        print(f"{m[0]} OFF")

        return True

    m = re.search("^([0-8a])name$", arg)
    if m:
        n = m.group(1)
        if norefresh and response:
            m = re.search(
                "<td.*?>([1-8])<\/td>.*?<\/td>[^\/]*?\W(ON|OFF)\W",
                response.content.decode("utf-8"),
                flags=re.MULTILINE | re.IGNORECASE,
            )
            if not m:
                ReLink("")
        else:
            RelLink("")

        content = response.content.decode("utf-8")

        if type == "lpc" and "<a href=outleto" in content:
            type = "epc"

        if m:
            if m.group(1) == 0 or n == "a":
                m = re.search(
                    '<th bgcolor="#DDDDFF" align=left>\s+Controller:\s+([^\<]*)',
                    content,
                )
                print(f'Controller: "{m.group(1).strip()}"')

        for m in re.findall(
            "<td.*?>([1-8])<\/td>\s*<td>(.*?)<\/td>[^\/]*?\W(ON|OFF)\W",
            content,
            flags=re.IGNORECASE | re.MULTILINE,
        ):
            if m[0] == n or n == "a":
                print(f'{m[0]}: "{m[1]}"')
        return True

    m = re.search("^([1-8a])power$", arg)
    if m:
        n = m.group(1)
        if norefresh and response:
            m = re.search(
                "<td.*?>([1-8])<\/td>.*?<\/td>[^\/]*?\W(ON|OFF)\W",
                response.content.decode("utf-8"),
                flags=re.MULTILINE | re.IGNORECASE,
            )
            if not m:
                ReLink("")
        else:
            RelLink("")

        content = response.content.decode("utf-8")

        if m:
            if n in ["1", "2", "3", "4", "a"]:
                m = re.search(
                    "<!--\s+RAW\s+VA=(\d+)\s+CA=(\d+)\s+VAH=(\S+)\s+CAH=(\S+)\s+(?:WHA100=(\S+)\s+)?-->",
                    content,
                    flags=re.IGNORECASE | re.MULTILINE,
                )
                vah = f"{m.group(3)}V" if float(m.group(3)) > 0 else "n/a"
                cah = f"{m.group(4)}A" if float(m.group(4)) > 0 else "n/a"
                wha = f"{float(m.group(5))/10.0}kWh" if float(m.group(5)) > 0 else "n/a"
                print(f"Bus A: V={vah} I={cah} W={wha}")
            if n in ["5", "6", "7", "8", "a"]:
                m = re.search(
                    "<!--\s+RAW\s+VB=(\d+)\s+CB=(\d+)\s+VBH=(\S+)\s+CBH=(\S+)\s+(?:WHB100=(\S+)\s+)?-->",
                    content,
                    flags=re.IGNORECASE | re.MULTILINE,
                )
                vbh = f"{m.group(3)}V" if float(m.group(3)) > 0 else "n/a"
                cbh = f"{m.group(4)}A" if float(m.group(4)) > 0 else "n/a"
                whb = f"{float(m.group(5))/10.0}kWh" if float(m.group(5)) > 0 else "n/a"
                print(f"Bus A: V={vbh} I={cbh} W={whb}")

        return True

    m = re.search("^arun(\d{1,3})$", arg)
    if m:
        n = int(m.group(1))
        if n < 1 or n > 127:
            return False
        RelLink(f"script?run{n:03d}")
        return True

    return False


if len(sys.argv) <= 1:
    usage()
(epc, auth) = sys.argv[1:3]
base = f"http://{auth}@{epc}/"

for arg in sys.argv[3:]:
    arg = arg.lower()

    if arg != "interact":
        if not cmd(arg):
            usage(f"ERROR: unknown command {arg}")
    else:
        print(prompt, end="", flush=True)
        for line in sys.stdin:
            line = line.strip()
            if line in ["?", "help"]:
                print(
                    "Commands: {?|help} | [n]{on|off|pulse|status|power|name} | runNNN | quit"
                )
            elif line == "quit":
                break
            elif cmd(line):
                print("\t[OK]")
            else:
                print("\t[ERROR]")
            print(prompt, end="", flush=True)
        print("")
