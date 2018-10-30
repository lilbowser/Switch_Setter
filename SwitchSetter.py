import logging
from datetime import time, timedelta, datetime, date
import time as time_p
import traceback

#import yaml
import requests


def scrapeSite(_url, use_progress_bar=False, retry=10):
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

    logging.debug("Scraping " + _url)
    try:
        website = requests.get(_url)
    except requests.Timeout as e:
        website = None
        if retry > 0:
            logging.warning("Retry #{}".format(11 - retry))
            time_p.sleep(0.25 * (11 - retry))
            retry_scrape = scrapeSite(_url, retry=(retry - 1))
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
        # printTKMSG("Uncaught Exception in scrapePlex", traceback.format_exc())

        if retry > 0:
            logging.warning("Retry #{}".format(11 - retry))
            time_p.sleep(0.33 * (11 - retry))
            retry_scrape = scrapeSite(_url, retry=(retry - 1))
            try:
                data = retry_scrape.text
            except:
                data = retry_scrape
            return data
        else:
            logging.error(traceback.format_exc())
            raise requests.RequestException

    if website is not None:
        website_data = website.text
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


if __name__ == '__main__':
    pass
