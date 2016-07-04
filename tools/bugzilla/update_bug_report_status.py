# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import bugzilla
import json
import configparser
import requests
import sys
import datetime

URL = "bugs.documentfoundation.org"

def update_bug_stats(session, bug_id, fixed):
    url = "http://crashreport.libreoffice.org/management/set-bug-status"

    data = {'fixed': fixed, 'bug_nr': bug_id}
    r = session.post(url, data = data)
    if r.status_code != 200:
        print("Error while setting tdf#%d to %s" % (bug_id, fixed))

def is_bug_report_fixed(bug):
    return not bug.is_open

def main():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    bzapi = bugzilla.Bugzilla(URL)
    bz_query_url = "https://bugs.documentfoundation.org/buglist.cgi?f1=cf_crashreport&f3=OP&f4=bug_status&f5=creation_ts&f6=cf_crashreport&j3=OR&list_id=620366&o1=isnotempty&o4=changedafter&o5=changedafter&o6=changedafter&query_format=advanced&v4=%s&v5=%s&v6=%s" % (yesterday.isoformat(), yesterday.isoformat(), yesterday.isoformat())
    query = bzapi.url_to_query(bz_query_url)

    bugs = bzapi.query(query)

    if len(bugs) == 0:
        sys.exit()

    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    login_url = "http://crashreport.libreoffice.org/accounts/login/"
    user = config["CrashReport"]["User"]
    password = config["CrashReport"]["Password"]
    session = requests.session()
    session.get(login_url)
    csrftoken = session.cookies['csrftoken']

    login_data = { 'username': user,'password': password,
            'csrfmiddlewaretoken': csrftoken }
    r1 = session.post(login_url, data=login_data, headers={"Referer": login_url})

    for bug in bugs:
        bug_id = bug.id
        fixed = is_bug_report_fixed(bug)
        try:
            update_bug_stats(session, bug_id, fixed)
        except Exception as e:
            print("exception setting bug status")
            print(e)

if __name__ == "__main__":
    main()

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
