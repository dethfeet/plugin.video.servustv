import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import urllib, urllib2
import pprint
import re
import urlparse
import brightcovePlayer

addon = xbmcaddon.Addon(id='plugin.video.servustv')

thisPlugin = int(sys.argv[1])
baseLink = "http://www.servustv.com/"

mediathekLink = baseLink + "cs/Satellite/VOD-Mediathek/001259088496198?p=1259088496182"
showLink = baseLink + "cs/Satellite?pagename=ServusTV/Ajax/MediathekData&nachThemen=all&nachSendung=%s&nachThemenNodeId=null&nachThemen_changed=1&nachSendung_changed=2&ajax=true"

height = 1080
const = "8e99dff8de8d8e378ac3f68ed404dd4869a4c007"
playerID = 1254928709001
publisherID = 900189268001

playerKey = "AQ~~,AAAA0Zd2KCE~,a1ZzPs5ODGffVvk2dn1CRCof3Ru_I9gE"

_regex_extractCategories = re.compile("<li class='category[0-9]{1}'><a href='(.*?)'>\r\n(.*?)</a></li>", re.DOTALL)
_regex_extractShows = re.compile("<select name=\"nachSendung\" id=\"nachSendung\">.*?</select>", re.DOTALL)
_regex_extractShow = re.compile("<option value='(.*?)'>(.*?)</option>")

_regex_extractShowNext = re.compile("<li><a href='(.*?)' class=\"nachste\">.*?</a></li>")

_regex_extractEpisode = re.compile("<li class='.*?'>.*?<a href='#' title='(.*?)'.*?<img src='(.*?)'.*?name=\"videoList\.subcategory\" value='([0-9]*)'/>.*?<div class=\"programDescription\">(.*?)</div>.*?</li>", re.DOTALL)

def mainPage():
    page = load_page(mediathekLink)
    
    for category in _regex_extractCategories.finditer(page):
        menu_link = category.group(1)
        menu_name = category.group(2)
        addDirectoryItem(menu_name, {"action" : "category", "link": menu_link})
    xbmcplugin.endOfDirectory(thisPlugin)

def showCategory(link):
    page = load_page(baseLink + urllib.unquote(link))
    
    shows = _regex_extractShows.search(page)
    
    menu_link = showLink % ("")
    menu_name = "Alle"
    addDirectoryItem(menu_name, {"action" : "show", "link": menu_link})
    
    for show in _regex_extractShow.finditer(shows.group(0)):
        menu_link = showLink % (show.group(1))
        menu_name = show.group(2)
        addDirectoryItem(menu_name, {"action" : "show", "link": menu_link})
    xbmcplugin.endOfDirectory(thisPlugin)

def showPage(link):
    page = load_page(urllib.unquote(link))
    
    for episode in _regex_extractEpisode.finditer(page):
        name = episode.group(1)
        url = episode.group(3)
        thumbnail = baseLink + episode.group(2)
        addDirectoryItem(name, {'action':"episode", 'link':url}, thumbnail, False)
    
    showMore = _regex_extractShowNext.search(page)
    if showMore is not None:
        menu_name = addon.getLocalizedString(30002)
        addDirectoryItem(menu_name, {"action" : "show", "link": baseLink + showMore.group(1)})
        
    xbmcplugin.endOfDirectory(thisPlugin)

def playEpisode(videoPlayer):
    brightcove_item = brightcovePlayer.play(const, playerID, str(videoPlayer), publisherID, height)
    stream_url = brightcove_item[1]
    rtmpbase = stream_url[0:stream_url.find("&")]
    playpath = stream_url[stream_url.find("&") + 1:]
    
    finalurl = rtmpbase + ' playpath=' + playpath
        
    item = xbmcgui.ListItem(path=finalurl)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def load_page(url):
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def addDirectoryItem(name, parameters={}, pic="", folder=True):
    li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
    if not folder:
        li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
                                
    return param


if not sys.argv[2]:
    mainPage()
else:
    params = get_params()
    if params['action'] == "category":
        showCategory(params['link'])
    elif params['action'] == "show":
        showPage(params['link'])
    elif params['action'] == "episode":
        playEpisode(params['link'])
    else:
        mainPage()
