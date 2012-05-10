# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VIDEO_PREFIX = "/video/prime7"
NAME = L('Title')
VERSION = 0.3
DEFAULT_CACHE_INTERVAL = 1800
OTHER_CACHE_INTERVAL = 300

ART           = 'prime7-background.jpg'
ICON          = 'icon-default.jpg'

BROWSE_URL = "http://au.tv.yahoo.com/plus7/browse/"
BASE = "http://au.tv.yahoo.com"
####################################################################################################

def Start():
    
    Log("In Start")
    
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
    
    HTTP.SetCacheTime(DEFAULT_CACHE_INTERVAL)

####################################################################################################


#setup the Main Video Menu - ie. get Top level categories
def VideoMainMenu():
    dir = MediaContainer(viewGroup="InfoList")
    myNamespaces = {'ns1':'http://www.w3.org/1999/xhtml'}
    xml = XML.ElementFromURL(BROWSE_URL,True)
    xpathQuery = "//li[.]"
    for Entry in xml.xpath(xpathQuery, namespaces=myNamespaces):
        show = {}
        try:
            Log("Trying to get title")
            show['Title'] = Entry.xpath("h3/a")[0].text
            Log("got title - continuing")
            show['Thumb'] = Entry.xpath("a[1]/img")[0].get('src')
            show['Url'] = Entry.xpath("h3/a")[0].get('href')
            Log("Found Title: " + show['Title'])
            Log("With Url: " + show['Url'])
            Log("With thumb: " + show['Thumb'])
            dir.Append(Function(DirectoryItem(SeriesMenu, title=show['Title'], thumb=show['Thumb']), ShowUrl=show['Url'], ShowTitle=show['Title']))
        except IndexError:
            Log ("Index error handled")
    return dir

def SeriesMenu(sender, ShowUrl, ShowTitle):
    dir = MediaContainer(title1="Prime7", title2=ShowTitle, viewGroup="InfoList")
    Log("Clicked on category item: " + ShowTitle)
    Log("Reading URL:**" + ShowUrl + "**")
    myNamespaces = {'ns1':'http://www.w3.org/1999/xhtml'}
    htmlResponse = XML.ElementFromURL(ShowUrl,isHTML=True,errors='ignore')
    #backGround = htmlResponse.xpath("id(\'bd\')/div[1]/div[2]/div[1]/div[2]/a", namespaces=myNamespaces)[0].get('href')
    #Log("background url " + backGround)
    #dir = MediaContainer(title1="Prime7", title2=ShowTitle, viewGroup="InfoList", art=backGround)
    #xpathQuery1 = "//div[.]/h3/a"
    xpathQuery1 = "//div[@class='itemdetails']"
    shows = htmlResponse.xpath(xpathQuery1)
    Log ("Try xpath results length" + str(len(shows)))
    for show in shows:
        inner = show.xpath("h3/a")
        if len(inner) > 0:
            inner = inner[0]
            video = {}
            video['ShowName'] = inner.xpath("span[@class='title']")[0].text
            Log("Found Show " + video['ShowName'])
        
            if video['ShowName'] == ShowTitle:
                temp = inner.xpath("span[@class='subtitle']/span")[0].text
                video['Url'] = BASE + inner.get('href')
                Log("Url" + video['Url'])
                Log(temp)
                video['Episode'] = inner.xpath("span[@class='subtitle']/span")[0].text
                video['Air Date'] = inner.xpath("span[@class='subtitle']")[0].text
                video['Summary'] = show.xpath("p")[0].text
                Log("Episode = " + str(video['Episode']))
                Log("Show = " + video['ShowName'])
                Log("we match")
                dir.Append(WebVideoItem(video['Url'], title=str(video['Episode']), summary=video['Summary']))
            else:
                Log("no match")
    
    Log("returning")
    return dir