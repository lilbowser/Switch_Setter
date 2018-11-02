"""

"""

import logging
from datetime import time, timedelta, datetime, date
import time as time_p
import traceback
import re
import sched

#import yaml
import requests


def scrapeSiteWithPost(_url, POST, use_progress_bar=False, retry=10):
    """
    Safely retrieves and returns a website using passed URL.
    If error occurs during retrieval, None will be returned instead
    @param _url: The URL of the website that will be scraped
    @type _url: str
    @param retry: Indicates How many retries are left. Starts at 10 by default.
    @type retry: int
    @return: website html if successful, otherwise None
    @rtype: str | None | requests.Response
    """

    logging.debug("POSTing: " + str(POST) + " , to: " + _url)
    try:
        website = requests.post(_url, json=POST)
    except requests.Timeout as e:
        website = None
        if retry > 0:
            logging.warning("Retry #{}".format(11 - retry))
            time_p.sleep(0.25 * (11 - retry))
            retry_scrape = scrapeSiteWithPost(_url, POST, retry=(retry - 1))
            try:
                data = retry_scrape.text
            except:
                data = retry_scrape
            return data
        else:
            logging.error(traceback.format_exc())
            raise requests.Timeout

    except Exception as error:
        website = None
        # printTKMSG("Uncaught Exception in scrape", traceback.format_exc())

        if retry > 0:
            logging.warning("Retry #{}".format(11 - retry))
            time_p.sleep(0.33 * (11 - retry))
            retry_scrape = scrapeSiteWithPost(_url, POST, retry=(retry - 1))
            try:
                data = retry_scrape.text
            except:
                data = retry_scrape
            return data
        else:
            logging.error(traceback.format_exc())
            raise requests.RequestException

    if website is not None:
        website_data = None
        if website.status_code == 200:
            website_data = website.text
        elif website.status_code == 500:
            website_data = "500_ISE"
        elif website.status_code == 422:
            # We are setting the new fronter to be the person who is already in front
            website_data = "422"
        else:
            raise Exception('Error retrieving web data')

    else:
        website_data = None

    return website_data


def load_config(uri="secrets.yaml"):
    import yaml
    with open(uri, 'r') as stream:
        try:
            _config = yaml.load(stream)
            return _config
        except yaml.YAMLError:
            logging.exception("Error loading yaml config")


def get_current_fronter(token):
    _post = {"webhook": {"command": "switch"}}
    results = scrapeSiteWithPost(token, _post, retry=0)
    if results is None:
        raise Exception("No Website Data") #  Should not be handled here
    elif results == "500_ISE":
        #MIGHT BE LIGIT SERVER ERORR OR NO ONE IS SWITCHED IN
        return "None", "1900-1-1T00:00:00.167Z"

    _name = re.match('{"member_name":"(\w+)"', results)
    if _name:
        _name = _name.groups()[0]

    _time = re.match('.*"started_at":"(.*)"', results)
    if _time:
        _time = _time.groups()[0]
    return _name, _time


def set_current_fronter(token, fronter):
    _post = {"webhook": {"command": "switch","member_name": fronter}}
    results = scrapeSiteWithPost(token, _post, retry=0)
    if results == "422":
        logging.warning("Fronter was already set.")
        return fronter
    _name = re.match('{"member_name":"(\w+)"', results)
    if _name:
        _name = _name.groups()[0]
    return _name

    # _time = re.match('.*"started_at":"(.*)"', results)
    # if _time:
    #     _time = _time.groups()[0]


def switch_out(_token):
    results = set_current_fronter(_token, "_nil")
    logging.info("Fronter has switched out")
    print("Fronter has switched out @ {}".format(datetime.today()))
    assert results == "_nil"


def find_next_time(_days_away=1, _hour=23, _minute=45):
    # Set by defualt for tomorrow @ 11:45
    current_date = date.today()
    tomorrow = current_date + timedelta(days=_days_away)

    bed_time = time(hour=_hour, minute=_minute)
    tomorrow_bed_time = datetime.combine(tomorrow, bed_time)
    sec_since_epoch = tomorrow_bed_time.timestamp()
    # return sec_since_epoch
    return tomorrow_bed_time


def abs_schedule(_token, _days_away=1):
    next_time = find_next_time(_days_away=_days_away, _hour=22, _minute=1)
    logging.info("Scheduling Next Switch-out for {}".format(next_time))
    s.enterabs(next_time.timestamp(), 1, switch_out, kwargs={'_token': _token})
    s.run()


if __name__ == '__main__':
    logging.basicConfig(format="[%(asctime)s] %(name)s: %(funcName)s:%(lineno)d %(levelname)s: %(message)s",
                        level=logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.DEBUG)

    logging.info("SwitchSetter.py has started")
    config = load_config("Config&Secrets.yaml")
    sc_token = config['token']

    s = sched.scheduler(time_p.time, time_p.sleep)

    logging.info("Starting Scheduler NOW! @ {}".format(datetime.today()))
    abs_schedule(sc_token, _days_away=0)
    while True:
        abs_schedule(sc_token)

    # current_fronter_name, Current_fronter_time = get_current_fronter(config['token'])
    # print("The current fronter is: {}".format(current_fronter_name))

    # switch_out(sc_token)


