
import sys
import requests
import configparser

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

    r = session.post(sys.argv[2])
    if r.status_code != 200:
        print("error calling %s" % sys.argv[2])

if __name__ == "__main__":
    main()

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
