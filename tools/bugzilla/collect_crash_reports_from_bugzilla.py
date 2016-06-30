import bugzilla
import json
import configparser
import requests
import sys
import datetime

URL = "bugs.documentfoundation.org"

def set_bug_to_report(session, signature, bug):
    url = "http://crashreport.libreoffice.org/management/add-bug"

    data = {'signature': signature, 'bug_nr': bug}
    r = session.post(url, data = data)
    if r.status_code != 200:
        print("Error while setting tdf#%d to %s" % (bug, signature))

def main():

    login_url = "http://crashreport.libreoffice.org/accounts/login/"

    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    user = config["CrashReport"]["User"]
    password = config["CrashReport"]["Password"]
    session = requests.session()
    session.get(login_url)
    csrftoken = session.cookies['csrftoken']

    login_data = { 'username': user,'password': password,
            'csrfmiddlewaretoken': csrftoken }
    r1 = session.post(login_url, data=login_data, headers={"Referer": login_url})

    bzapi = bugzilla.Bugzilla(URL)

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    bz_query_url = "http://bugs.documentfoundation.org/buglist.cgi?f1=cf_crashreport&f2=cf_crashreport&o1=isnotempty&o2=changedafter&product=LibreOffice&query_format=advanced&v2=%s" % yesterday.isoformat()
    print(bz_query_url)
    query = bzapi.url_to_query(bz_query_url)

    bugs = bzapi.query(query)
    for bug in bugs:

        bug_id = bug.id
        crash_report_entry = bug.cf_crashreport
        if crash_report_entry.strip().startswith("["):
            try:
                crash_reports = json.loads(bug.cf_crashreport)
                for crash_report in crash_reports:
                    set_bug_to_report(session, crash_report, bug_id)
            except Exception as e:
                print(e)
        else:
            print(bug_id)
            print(crash_report_entry)


if __name__ == "__main__":
    main()

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
