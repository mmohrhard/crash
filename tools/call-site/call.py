
import sys
import requests
import configparser

base_address = "http://crashreport.libreoffice.org/"

def main():

    login_url = base_address + "accounts/login/"

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

    url = base_address + sys.argv[2]
    r = session.post(url)
    if r.status_code != 200:
        print("error calling %s" % url)

if __name__ == "__main__":
    main()

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
