import urllib2
from cookielib import CookieJar
import shazam_api
import re
import json
import HTMLParser
import shazam_parser

html_parser = HTMLParser.HTMLParser()
get_all = False


def normalize_str(elem):
    norm = re.sub(r'/', '-', elem)
    norm = re.sub(r'[/",;\?]+', '', norm)
    norm = re.sub(r'&', 'and', norm)
    norm = re.sub(r'\(.+\)', '', norm)
    norm = norm.strip()
    if norm[0:3] == "by ":
        norm = norm[3:]
    return norm


def add_proper_headers(http_req, accept, referer, cookie = ""):
    http_req.add_header('User-Agent', "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0")
    http_req.add_header('Accept', accept)
    http_req.add_header('Accept-Language', "fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3")
    http_req.add_header('Connection', "keep-alive")
    http_req.add_header('Referer', referer)
    if cookie != "":
        http_req.add_header('Cookie', cookie)


def get_shazam_tags(fat_cookie, uid_cookie):
    my_tags = []
    req = urllib2.Request("http://www.shazam.com/fragment/myshazam?size=large")
    add_proper_headers(req,
                       accept="application/json, text/javascript, */*; q=0.01",
                       referer="http://www.shazam.com/myshazam",
                       cookie="fat=" + fat_cookie + "; uid=" + uid_cookie + ";"
                       )

    resp = urllib2.urlopen(req).read()
    json_content = json.loads(resp)['feed']

    if not get_all:
        all_tags = shazam_parser.parse( html_parser.unescape(json_content) )
        delay_to_keep = 60*30
    else:
        print 'Getting all shazam tags ...'
        all_tags = []
        tmp_resp = resp
        tmp_json = json_content
        tmp_tags = shazam_parser.parse( html_parser.unescape(json_content) )
        next_url = "http://www.shazam.com" + str(json.loads(resp)['previous']) + '&size=large'
        while True:
            all_tags += tmp_tags
            if len(next_url) < 200:
                break
            else:
                req = urllib2.Request(next_url)
                add_proper_headers( req,
                                    accept = "application/json, text/javascript, */*; q=0.01",
                                    referer = "http://www.shazam.com/myshazam",
                                    cookie = "fat=" + fat_cookie + "; uid=" + uid_cookie + ";"
                                  )
                tmp_resp = urllib2.urlopen(req).read()
                tmp_json = json.loads(tmp_resp)['feed']
                tmp_tags = shazam_parser.parse( html_parser.unescape(tmp_json) )
                next_url = "http://www.shazam.com" + str(json.loads(tmp_resp)['previous']) + '&size=large'

        delay_to_keep = float("inf")
        print 'Done ! (' + str(len(all_tags)) + ' tags)' + '\n'

    for tag in all_tags:
            artist = normalize_str(tag[0])
            title = normalize_str(tag[1])
            delay = tag[2]
            filename = title + '-' + artist + ".mp3"
            # if { 'artist' : artist, 'title' : title } not in my_tags and filename not in already_dl and delay < delay_to_keep:
            my_tags += [{ 'artist' : artist, 'title' : title, 'filename' : filename }]
    return my_tags
