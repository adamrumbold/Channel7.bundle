# PMS plugin framework
####################################################################################################

VIDEO_PREFIX = "/video/channel7"
NAME = L('Title')
DEFAULT_CACHE_INTERVAL = 1800
OTHER_CACHE_INTERVAL = 300
ART           = 'prime7-background.jpg'
ICON          = 'channel7.png'
BROWSE_URL = "http://au.tv.yahoo.com/plus7/browse/"
BASE = "http://au.tv.yahoo.com"
####################################################################################################

def Start():
    
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
        
####################################################################################################
@route(VIDEO_PREFIX + '/home')
def VideoMainMenu():
    cookies = HTTP.CookiesForURL("http://au.tv.yahoo.com")
    oc = ObjectContainer(title2='Prime7 On Demand', view_group='List')
    
    xml = HTML.ElementFromURL(BROWSE_URL, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'})
    for Entry in xml.xpath("//*[@id='atoz']/ul/li"):
        show = {}
        try:
            
            show['Title'] = Entry.xpath("h3/a")[0].text
            show['Thumb'] = Entry.xpath("a[1]/img")[0].get('src')
            show['Url'] = Entry.xpath("h3/a")[0].get('href')
            Log('Got show: ' + show['Title'])
            Log('Got Url: ' + show['Url'])
            Log('Got thumb: ' + show['Thumb'])
            oc.add(DirectoryObject(
                key=Callback(SeriesMenu, ShowUrl=show['Url'], ShowTitle=show['Title']),
                title=show['Title'],
                thumb=show['Thumb'],
            ))
        except IndexError:
            Log.Debug ("failed parsing " + str(show) )
    Log("Returning OC")    
    return oc

@route(VIDEO_PREFIX + '/show')
def SeriesMenu(ShowUrl, ShowTitle):
    Log("In series menu")
    oc = ObjectContainer(title2=ShowTitle, view_group='InfoList')
    htmlResponse = HTML.ElementFromURL(ShowUrl)
    shows = htmlResponse.xpath("//div[@class='itemdetails']")
    for show in shows:
        inner = show.xpath("h3/a")
        if len(inner) > 0:
            inner = inner[0]
            video = {}
            video['ShowName'] = inner.xpath("span[@class='title']")[0].text
            if video['ShowName'] == ShowTitle:
                video['Url'] = BASE + inner.get('href')
                video['Air Date'] = inner.xpath("span[@class='subtitle']")[0].text
                try:
                    video['Episode'] = inner.xpath("span[@class='subtitle']/span")[0].text
                except:
                    video['Episode'] = inner.xpath("span[@class='subtitle']")[0].text
                try:
                    video['Summary'] = show.xpath("p")[0].text
                except:
                    video['Summary'] = "unknown"
                vco = VideoClipObject(
                        url= video['Url'], 
                        title=video['Episode'],
                        summary=video['Summary'],
                     )
                oc.add(vco)
            else:
                pass
    return oc