#!/usr/bin/env python

from datetime import datetime, timedelta
from email.mime.text import MIMEText
import subprocess
import smtplib
import csv
import re

report_to = 'you@example.com'
report_from = 'fail2ban@example.com'

msg_header = """
SSH Ban Report
==============
"""
ip_list = ''

yesterday = datetime.now() - timedelta(days=1)
yesterday = yesterday.strftime('%Y-%m-%d')

with open("/etc/fail2ban/blacklist.csv", "rb") as blacklist_file:
    blacklist = csv.DictReader(blacklist_file)
    for record in blacklist:
        if record['DATE'] == yesterday:
            whois = subprocess.Popen(['whois', record['IP_ADDRESS']],
                                     stdout=subprocess.PIPE)
            whois.wait()
            find_country = re.search(r'country:(.*)', whois.communicate()[0])
            if find_country:
                ip_list += ("%s: %s\n" % (record['IP_ADDRESS'],
                                          find_country.group(1).strip()))
            else:
                ip_list += ("%s: unknown\n" % record['IP_ADDRESS'])

if ip_list:
    template = msg_header + ip_list
else:
    template = msg_header + "No Banned IPs for this report date"

try:
    msg = MIMEText(template)
    msg['Subject'] = 'SSH Ban Report'
    msg['From'] = report_from
    msg['To'] = report_to

    s = smtplib.SMTP('localhost')
    s.sendmail(report_from, [report_to], msg.as_string())
    s.quit()
except Exception as e:
    print(e)
