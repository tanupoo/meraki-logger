import re
from datetime import datetime
from dateutil.parser import parse as dtparse
from dateutil.tz import gettz

re_nots = re.compile("(\S+) (?P<t2>\S+) (?P<msg>.*)")
re_ev = re.compile("(?P<ap_name>\S+) "
                   "(?P<log_type>\S+) "
                   "type=(?P<ev_type>\S+) "
                   "(?P<detail>.*)")
re_kv = re.compile("(\w+)(=('([^']+)'|(\S+))|)")

float_types = """
duration
auth_neg_dur
last_auth_ago
full_conn
ip-resp
http_resp
arp_resp
dns_req_rtt
dns_resp
""".splitlines()[1:]

"""
The form of the message must be like below:

2023-06-15T13:13:51.136: INFO: <134>1 1686802430.724431243 MR36_98_18_88_c0_78_84 events type=8021x_eap_success ...
"""
class parser():

    def __init__(self, error_file="error.log", tzstr="Asia/Tokyo",
            embed_syslog=True):
        self.error_file = error_file
        self.tzstr = tzstr
        self.embed_syslog = embed_syslog

    def putlog(self, msg):
        with open(self.error_file, "a+") as fd:
            print(msg, file=fd)

    def parse(self, line):
        line = line.strip()
        if not self.embed_syslog:
            line = " ".join(line.split()[2:])
        if "Listen on:" in line:
            self.putlog(f"IGNORE LINE: {line}")
            return None
        # parse the timestamp.
        dt1 = datetime.now(tz=gettz(self.tzstr))
        r = re_nots.match(line)
        if not r:
            self.putlog(f"IGNORE re_ts: {line}")
            return None
        t2 = r.group("t2")
        try:
            dt2 = datetime.fromtimestamp(float(t2), tz=gettz(self.tzstr))
        except ValueError:
            self.putlog(f"IGNORE ttl: {line}")
            return None
        ttl = (dt1 - dt2).total_seconds()
        msg = r.group("msg")
        # parse the event type.
        if "cli_set_rad_parms" in msg:
            self.putlog(f"IGNORE event type: {line}")
            return None
        r = re_ev.match(msg)
        if not r:
            self.putlog(f"IGNORE re_ev: {line}")
            return None
        detail = r.group("detail")

        # init the event.
        ev_one = {
            "ts": dt2.isoformat(),
            "ap_name": r.group("ap_name"),
            "log_type": r.group("log_type"),
            "ev_type": r.group("ev_type"),
            "ttl": ttl,
            }

        # parse the detail.
        for r in re_kv.findall(detail):
            k = r[0]
            if r[3] != '':
                ev_one.update({k:r[3]})
            elif r[4] != '':
                ev_one.update({k:r[4]})
            else:
                # ignore the key
                self.putlog(f"IGNORE KEY: {k} in {line}")

        return ev_one

