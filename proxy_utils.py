# -*- coding: utf-8 -*-
"""
Created on: 04-Jan-2022
Author: VonMasso

Functions to get proxy, and start webscraping
this function piggybacks of requests to determine the proxy ID
I have then integrated this function into the get requests to solve any proxy issues
The output of this function can be parsed with any html parser, including beautiful soup

"""

import re
import warnings

import requests

warnings.filterwarnings("ignore")


def get_proxy(cibc_proxy_pool="http://globalproxy:8081/proxy.pac",
              cibc_proxy_tail=".net.ca.cibcwm.com:8080"):
    """

    :param cibc_proxy_pool:     :default, the path to the proxy file, the list of all possible
    proxies to be indexed
    :param cibc_proxy_tail:     :the tail, after the proxy ID, this can be found in the proxy.pac
    file and generally goes unchanged
    :return:                    :the proxy ID
    """
    proxy_find = requests.get(cibc_proxy_pool)
    proxy_ids = set(re.findall(r"([a-z0-9]+)-p2i", proxy_find.text)[:])
    print("=" * 65 + "\n" + "Looping through possible proxies..." + "\n" + "-" * 65)
    for proxy_id in proxy_ids:

        proxy_uri = proxy_id.upper() + cibc_proxy_tail
        try:
            sess = requests.Session()
            sess.proxies = {"http": proxy_uri, "https": proxy_uri}
            _ = requests.get("https://google.com", proxies={"http": proxy_uri, "https": proxy_uri},
                             verify=False)
            print("You are connected to %s proxy" % proxy_uri)
            print("=" * 65)
            return proxy_uri

        except OSError:
            pass

    return None


def use_proxy(url, cibc_proxy_pool="http://globalproxy:8081/proxy.pac",
               cibc_proxy_tail=".net.ca.cibcwm.com:8080"):
    """

    :param url:                 :the url you want to scrape
    :param cibc_proxy_pool:
    :param cibc_proxy_tail:
    :return:                    :the scraped text
    """

    proxy = get_proxy(cibc_proxy_pool, cibc_proxy_tail)
    try:
        sess = requests.Session()
        sess.proxies = {"http": proxy, "https": proxy}
        response = requests.get(url.replace(" ", "+"), proxies={"http": proxy, "https": proxy},
                                verify=False)

        rsp = response.text.lower()
        if ("<title>" in rsp) and ("</title>" in rsp):
            access_mode = rsp.split("<title>")[1].split("</title>")[0]
            if access_mode == "access denied":
                print("[X] Access Denied for %s" % url)
                return None

        print("[O] Scraped: %s" % url)
        return response.text

    except ConnectionError:
        print("[X] Failed to scrape: %s" % url)
        return None