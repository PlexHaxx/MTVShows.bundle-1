TITLE = 'MTV Shows'
PREFIX = '/video/mtvshows'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.mtv.com'
SHOWS = 'http://www.mtv.com/ontv'
SHOWS_AZ = 'http://www.mtv.com/shows/azfilter?template=/shows/home2/modules/azFilter&startingCharac=%s&resultSize=50'
MTV_POPULAR = 'http://www.mtv.com/most-popular/%smetric=numberOfViews&range=%s&order=desc'
# The three variables below produce the results page for videos for shows with the new format
ALL_VID_AJAX = 'http://www.mtv.com/include/shows/seasonAllVideosAjax?id=%s&seasonId=%s&resultSize=1000&template=/shows/platform/watch/modules/seasonRelatedPlaylists&start=0'
FULL_EP_AJAX = 'http://www.mtv.com/shows/seasonAllVideosAjax?device=desktop&id=%s&seasonId=%s&filter=fullEpisodes&template=/shows/platform/watch/modules/episodePlaylists'
BUILD_URL = 'http://www.mtv.com/video/?id='

RE_SEASON  = Regex('Season (\d{1,2})')
RE_EP = Regex('\| Ep. (\d{1,3})')
RE_VIDID = Regex('#id=(\d{7})')
# episode regex for new show format
RE_EXX = Regex('/e(\d+)')
LATEST_VIDEOS = [
    {'title'  : 'Latest Full Episodes',  'url'  : 'http://www.mtv.com/videos/home.jhtml'},
    {'title'  : 'Latest Music Videos',   'url'  : 'http://www.mtv.com/music/videos/'},
    {'title'  : 'Latest Movie Trailers',  'url'  : 'http://www.mtv.com/movies/trailer_park/'}
]
# The latest interviews do not fit into the current video page format, so we have removed them
#    {'title'  : 'Latest Movie Interviews',   'url'  : 'http://www.mtv.com/movies/features_interviews/morevideo.jhtml'}
MOST_POPULAR = [
    {'title'  : 'All Videos',  'video_type'  : 'videos/?'},
    {'title'  : 'Full Episodes',   'video_type'  : 'tv-show-videos/?category=full-episodes&'},
    {'title'  : 'After Shows',  'video_type'  : 'tv-show-videos/?category=after-shows&'},
    {'title'  : 'Show Clips',  'video_type'  : 'tv-show-videos/?category=bonus-clips&'},
    {'title'  : 'All Music Videos',   'video_type'  : 'music-videos/?'},
    {'title'  : 'Pop & Rock Music Videos',  'video_type'  : 'music-videos/?category=pop&'},
    {'title'  : 'Hip Hop Music Videos',  'video_type'  : 'music-videos/?category=hip-hop&'},
    {'title'  : 'Movie Trailers',   'video_type'  : 'movie-trailers/?'},
    {'title'  : 'Movie Interviews',  'video_type'  : 'movie-clips/?'}
]
# Specials Archive List
SPECIAL_ARCHIVES = [
    {'title'  : 'Video Music Awards',  'url'  : 'http://www.mtv.com/ontv/vma/archive/'},
    {'title'  : 'Movie Awards',   'url'  : 'http://www.mtv.com/ontv/movieawards/archive/'},
    {'title'  : 'mtvU Woodie Awards',  'url'  : 'http://www.mtv.com/ontv/woodieawards/archive/'}
]

####################################################################################################
# Set up containers for all possible objects
def Start():

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    EpisodeObject.thumb = R(ICON)
    VideoClipObject.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR 
 
#####################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(MTVShows, title='MTV Shows'), title='MTV Shows')) 
    oc.add(DirectoryObject(key=Callback(MTVVideos, title='MTV Videos'), title='MTV Videos')) 
    oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.mtvshows", title=L("Search MTV Videos"), prompt=L("Search for Videos")))
    return oc
#######################################################################################
# This is a function that only returns show urls to provide users easier access to archived shows
# This function uses the "All Results" section of the MTV search URL and only returns URLs that end with series.jhtml
# THIS DOES NOT USE OR INTERACT WITH THE SEARCH SERVICE FOR VIDEOS AND IS A COMPLETELY SEPARATE FUNCTION
@route(PREFIX + '/showsearch')
def ShowSearch(query):
    oc = ObjectContainer(title1='MTV', title2='Show Search Results')
    url = '%s/search/?q=%s' %(BASE_URL, String.Quote(query, usePlus = True))
    html = HTML.ElementFromURL(url)
    for item in html.xpath('//div[@id="searchResults"]/ul/li'):
        link = item.xpath('.//a/@href')[0]
        # This make sure it only returns show pages by making sure the url starts with www.mtv.com/shows/ that may contain /season_?/ and ends with / or series.jhtml
        try:
            season = 0
            url_part = link.split('http://www.mtv.com/shows/')[1]
            if 'season_' in url_part:
                season = int(url_part.split('season_')[1].split('/')[0])
                url_test = url_part.split('/')[2]
            else:
                url_test = url_part.split('/')[1]
            if not url_test or url_test=='series.jhtml':
                title = item.xpath('./div[contains(@class,"mtvn-item-content")]//a//text()')[0]
                thumb = item.xpath('.//img/@src')[0].split('?')[0]
                # Most shows are listed by individual season in the show search unless new format
                if link.endswith('series.jhtml'):
                    oc.add(DirectoryObject(key=Callback(ShowOldSections, title=title, thumb=thumb, url=link, season=season), title=title, thumb = thumb))
                else:
                    oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, thumb=thumb, url=link), title=title, thumb = thumb))
        except:
            continue
    return oc

#####################################################################################
# For MTV main sections of Popular, Specials, and All Shows
@route(PREFIX + '/mtvshows')
def MTVShows(title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(ProduceShows, title='Current MTV Shows'), title='Current MTV Shows')) 
    # The MTV2 currents shows link ('http://www.mtv.com/ontv/all/currentMtv2.jhtml') could also be used with AllShows() function
    oc.add(DirectoryObject(key=Callback(ProduceShows, title='Current MTV2 Shows'), title='Current MTV2 Shows')) 
    oc.add(DirectoryObject(key=Callback(ProduceSpecials, title='MTV Specials'), title='MTV Specials')) 
    oc.add(DirectoryObject(key=Callback(Alphabet, title='Shows A to Z'), title='Shows A to Z'))
    # THE MENU ITEM BELOW CONNECTS TO A FUNCTION WITHIN THIS CHANNEL CODE THAT PRODUCES A LIST OF SHOWS FOR USERS 
    # IT DOES NOT USE OR INTERACT WITH THE SEARCH SERVICES FOR VIDEOS LISTED NEXT
    #To get the InputDirectoryObject to produce a search input in Roku, prompt value must start with the word "search"
    oc.add(InputDirectoryObject(key=Callback(ShowSearch), title='Search for MTV Shows', summary="Click here to search for shows", prompt="Search for the shows you would like to find"))
    return oc
#####################################################################################
# For MTV main sections of Videos
@route(PREFIX + '/mtvvideos')
def MTVVideos(title):
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key=Callback(LatestVideos, title='Latest Videos'), title='Latest Videos')) 
    oc.add(DirectoryObject(key=Callback(MostPopularVideos, title='Most Popular Videos'), title='Most Popular Videos')) 
    return oc
#####################################################################################
# For main sections of Latest Videos
@route(PREFIX + '/latestvideos')
def LatestVideos(title):
    oc = ObjectContainer(title2=title)
    for items in LATEST_VIDEOS:
        title = items['title']
        # Skip full episodes for Android Clients
        if "Full Episodes" in title and Client.Platform in ('Android'):
            continue
        url = items['url']
        oc.add(DirectoryObject(key=Callback(VideoPage, title=title, url=url), title=title)) 
    return oc
#####################################################################################
# For main sections of Most Popular Videos
@route(PREFIX + '/mostpopularvideos')
def MostPopularVideos(title):
    oc = ObjectContainer(title2=title)
    for items in MOST_POPULAR:
        title = items['title']
        # Skip full episodes for Android Clients
        if "Full Episodes" in title and Client.Platform in ('Android'):
            continue
        video_type = items['video_type']
        oc.add(DirectoryObject(key=Callback(MostPopularSections, title=title, video_type=video_type), title=title)) 
    return oc
####################################################################################################
# MTV Popular Split by day week and month
@route(PREFIX + '/mostpopularsections')
def MostPopularSections(title, video_type):
    oc = ObjectContainer(title2=title)
    time = ["today", "week", "month"]
    oc.add(DirectoryObject(key=Callback(VideoPage, url = MTV_POPULAR %(video_type, time[0]), title="Most Popular Today"), title="Most Popular Today"))
    oc.add(DirectoryObject(key=Callback(VideoPage, url = MTV_POPULAR %(video_type, time[1]), title="Most Popular This Week"), title="Most Popular This Week"))
    oc.add(DirectoryObject(key=Callback(VideoPage, url = MTV_POPULAR %(video_type, time[2]), title="Most Popular This Month"), title="Most Popular This Month"))
    return oc
#####################################################################################
# For Producing Popular Shows 
@route(PREFIX + '/produceshows')
def ProduceShows(title):
    oc = ObjectContainer(title2=title)
    if 'MTV2' in title:
        (xpath, xpath2) = ('content-box', 'text-block')
        local_url = BASE_URL + '/mtv2/'
    else:
        (xpath, xpath2) = ('item promo-block', 'header')
        local_url = BASE_URL + '/shows'
    data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)

    for video in data.xpath('//div[@class="%s"]/a' %xpath):
        url = video.xpath('./@href')[0]
        if not url.startswith('http://'):
            url = BASE_URL + url
        title = video.xpath('.//div[@class="%s"]/span//text()' %xpath2)[0].title()
        title = title.replace('&#36;', '$')
        try: thumb = video.xpath('.//div[contains(@class,"thumb")]/@data-src')[0]
        except: thumb = video.xpath('.//img/@src')[0].split('?')[0]
        if '/shows/' in url:
            # These shows have a bad url, so fix it first
            if '/teen_mom_2/series.jhtml' in url or '/awkward/series.jhtml' in url or '/friendzone/series.jhtml' in url or '/truelife/series.jhtml' in url:
                url = url.split('series.jhtml')[0]
            # This is for those shows with old format
            if url.endswith('series.jhtml'):
                oc.add(DirectoryObject(key=Callback(ShowOldSections, title=title, thumb=thumb, url=url), title=title, thumb = thumb))
            else:
                oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, thumb=thumb, url=url), title=title, thumb = thumb))

    oc.objects.sort(key = lambda obj: obj.title)

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are shows to list right now.")
    else:
        return oc
#####################################################################################
# For Producing a to z list of shows
@route(PREFIX + '/alphabet')
def Alphabet(title):
    oc = ObjectContainer(title2=title)
    for ch in list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        url=SHOWS_AZ %ch
        oc.add(DirectoryObject(key=Callback(ShowsAZ, title=ch, url=url), title=ch))
    return oc
#####################################################################################
# For Producing a to z list of shows
@route(PREFIX + '/showsaz')
def ShowsAZ(title, url):
    oc = ObjectContainer(title2=title)
    data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    for items in data.xpath('//ul/li/a'):
        url = BASE_URL + items.xpath('./@href')[0]
        title = items.xpath('.//text()')[0]
        if url=='#':
            continue
        if 'series.jhtml' in url:
            if 'jersey'in url:
                oc.add(DirectoryObject(key=Callback(ShowOldSections, title=title, url=url, season=0), title=title))
                continue
            url = url.split('series.jhtml')[0]
        oc.add(DirectoryObject(key=Callback(ShowSeasons, title=title, url=url), title=title))
    return oc
#####################################################################################
# For Producing the Specials Archive list of shows
@route(PREFIX + '/producespecials')
def ProduceSpecials(title):
    oc = ObjectContainer(title2=title)
    for specials in SPECIAL_ARCHIVES:
        url = specials['url']
        title = specials['title']
        oc.add(DirectoryObject(key=Callback(SpecialSections, title=title, url=url), title=title))
    return oc
#######################################################################################
# This function produces sections for shows with old table format
@route(PREFIX + '/showoldsections', season=int)
def ShowOldSections(title, url, thumb='', season=0):
    oc = ObjectContainer(title2=title)
    local_url = url.replace('series', 'video')
    data = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
    # First check to make sure there are videos for this show
    # FOUND THAT SOME DO NOT HAVE A WATCH VIDEO LINK ON THE SIDE BUT ALL HAVE WATCH VIDEO IN THE TITLE OF THE VIDEO PAGE
    video_check = data.xpath('//div/h1//text()')[0]
    if video_check:
        # This is for those shows that have sections listed below Watch Video
        for section in data.xpath('//li[contains(@class,"-subItem")]/div/a'):
            section_title = section.xpath('.//text()')[2].strip()
            section_url = BASE_URL + section.xpath('./@href')[0]
            oc.add(DirectoryObject(key=Callback(VideoPage, title=section_title, url=section_url, season=season), title=section_title, thumb=thumb))
        # Add a section to show all videos
        oc.add(DirectoryObject(key=Callback(VideoPage, title='All Videos', url=local_url, season=season), title='All Videos', thumb=thumb))
    # This handles pages that do not have a Watch Video section
    else:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos listed for this show.")
    return oc
#######################################################################################
# This function produces sections for shows with new format
@route(PREFIX + '/showseasons')
def ShowSeasons(title, url, thumb=''):
    oc = ObjectContainer(title2=title)
    local_url = url + 'video/'
    html = HTML.ElementFromURL(local_url, cacheTime = CACHE_1HOUR)
    new_season_list = html.xpath('//span[@id="season-dropdown"]//li/a')
    if len(new_season_list)> 0:
        for section in new_season_list:
            title = section.xpath('./span//text()')[0].strip().title()
            season = int(title.split()[1])
            season_id = section.xpath('./@data-id')[0]
            oc.add(DirectoryObject(key=Callback(ShowSections, title=title, thumb=thumb, url=local_url, season=season, season_id=season_id), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))
    else:
        # COULD GET THE SEASON FROM THE FIRST VIDEO HERE WITH REGEX IF THE SEASON WAS WANTED
        oc.add(DirectoryObject(key=Callback(ShowSections, title='Current Season', thumb=thumb, url=local_url, season=0), title='Current Season', thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)))

    # This handles pages that do not have a Watch Video section
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos listed for this show.")
    else:
        return oc
#######################################################################################
# This function produces sections for new show format
@route(PREFIX + '/showsections', season=int)
def ShowSections(title, thumb, url, season, season_id=''):
    oc = ObjectContainer(title2=title)
    html = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    section_list = html.xpath('//span[@id="video-filters-dropdown"]//li/a')
    for section in section_list:
        id = section.xpath('./@data-seriesid')[0]
        url = BASE_URL + section.xpath('./@href')[0]
        section_title = section.xpath('./span/text()')[0].title()
        if 'Full Episodes' in section_title:
            new_url = FULL_EP_AJAX
        else:
            new_url = ALL_VID_AJAX
        if season_id:
            new_url = new_url %(id, season_id)
        else:
            new_url = url
        oc.add(DirectoryObject(key=Callback(ShowVideos, title=section_title, url=new_url, season=season), title=section_title, thumb=thumb))
    return oc
#######################################################################################
# This function produces videos for the new show format
# LIMITING RESULTS PER PAGE DOES NOT SEEM TO WORK SO REMOVED PAGING
# FOR NOW I HAVE CHOSEN TO NOT SHOW RESULTS THAT HAVE "NOT AVAILABLE" BUT INCLUDE THOSE THAT GIVE A DATE FOR WHEN IT WILL BE AVAILABLE
@route(PREFIX + '/showvideos', season=int, start=int)
def ShowVideos(title, url, season):

    oc = ObjectContainer(title2=title)
    try: data = HTML.ElementFromURL(url)
    except: return ObjectContainer(header="Empty", message="There are no videos to list right now.")
    video_list = data.xpath('//div[contains(@class,"grid-item")]')
    for video in video_list:
        try: vid_avail = video.xpath('.//div[@class="message"]//text()')[0]
        except: vid_avail = 'Now'
        # Full episodes have a sub-header field for the title but all videos have a second header hidden text
        try: vid_title = video.xpath('.//div[@class="sub-header"]/span//text()')[0].strip()
        except: vid_title = video.xpath('.//div[@class="header"]/span[@class="hide"]//text()')[0].strip()
        thumb = video.xpath('.//div[@class=" imgDefered"]/@data-src')[0]
        seas_ep = video.xpath('.//div[@class="header"]/span//text()')[0].strip()
        if vid_avail == 'not available':
            continue
        if vid_avail == 'Now':
            vid_type = video.xpath('./@data-filter')[0]
            # Skip full episodes for Android Clients
            if vid_type=="FullEpisodes" and Client.Platform in ('Android'):
                continue
            vid_url = video.xpath('./a/@href')[0]
            # One descriptions is blank and gives an error
            try: desc = video.xpath('.//div[contains(@class,"deck")]/span//text()')[0].strip()
            except: desc = None
            other_info = video.xpath('.//div[@class="meta muted"]/small//text()')[0].strip()
            duration = Datetime.MillisecondsFromString(other_info.split(' - ')[0])
            date = Datetime.ParseDate(video.xpath('./@data-sort')[0])
            try: episode = int(RE_EXX.search(seas_ep).group(1))
            except: episode = None
            # This creates a url for playlists of video clips
            if '#id=' in url:
                id_num = RE_VIDID.search(vid_url).group(1)
                new_url = BUILD_URL + id_num
                vid_url = new_url

            oc.add(EpisodeObject(
                url = vid_url, 
                season = season,
                index = episode,
                title = vid_title, 
                thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
                originally_available_at = date,
                duration = duration,
                summary = desc
            ))
        else:
            avail_date = vid_avail.split()[1]
            avail_title = 'NOT AVAILABLE UNTIL %s' %avail_date
            desc = '%s - %s' %(seas_ep, vid_title)
            oc.add(PopupDirectoryObject(key=Callback(NotAvailable, avail=vid_avail), title=avail_title, summary=desc, thumb=thumb))
      
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos available to watch." )
    else:
        return oc
####################################################################################################
# This produces videos for most popular as well for specials
@route(PREFIX + '/videopage', season=int)
def VideoPage(url, title, season=0):
    oc = ObjectContainer(title2=title)
    id_num_list = []
    data = HTML.ElementFromURL(url)
    for item in data.xpath('//li[@itemtype="http://schema.org/VideoObject"]'):
        # This pulls data for show videos in table format
        try:
            link = item.xpath('./@mainurl')[0]
            video_title = item.xpath('./@maintitle')[0]
            image = item.xpath('./meta[@itemprop="thumbnail"]/@content')[0].split('?')[0]
            date = item.xpath('./@mainposted')[0]
            desc = item.xpath('./@maincontent')[0]
            # Some videos are locked or unavailable but still listed on the site
            # most have 'class="quarantineDate"' in, the description, but not all so using the text also
            if 'quarantineDate' in desc or 'Not Currently Available' in desc:
                continue
        # This pulls data for all other types of videos
        except:
            link = item.xpath('.//a/@href')[0]
            video_title = item.xpath('.//meta[@itemprop="name"]/@content')[0].strip()
            image = item.xpath('.//*[@itemprop="thumbnail" or @class="thumb"]/@src')[0].split('?')[0]
            try: date = item.xpath('.//time[@itemprop="datePublished"]//text()')[0]
            except: date = ''
            desc = None

        if 'hrs ago' in date or 'today' in date or 'hr ago' in date:
            date = Datetime.Now()
        else:
            date = Datetime.ParseDate(date)
        if not image.startswith('http:'):
            image = BASE_URL + image
        # THIS PREVENTS ERRORS FROM SOME SHOW PAGES LISTED ON THE LATEST FULL EPISODES VIDEO PAGE
        if '/video.jhtml' in link or '/video/full-episodes/' in link:
            continue
        # Here we start building the url
        if not link.startswith('http:'):
            link = BASE_URL + link
        # This handles playlists of video clips. They end with #id and a 7 digit number
        if '#id=' in link:
            # We first check to see if the id_num has been processed so we do not have multiple listings of the same playlist
            id_num = RE_VIDID.search(link).group(1)
            if id_num not in id_num_list:
                id_num_list.append(id_num)
                new_url = BUILD_URL + id_num
            else:
                continue
        else:
            new_url = link
            
        # Skip full episodes for Android Clients
        # Video clip playlists will only play the first clip for Android Clients
        if Client.Platform in ('Android') and 'playlist.jhtml' in new_url:
            continue

        # check for episode and season in code or the title
        try: episode = item.xpath('.//li[@class="list-ep"]//text()')[0]
        except: episode = 'xx'
        if episode.isdigit()==False:
            try:  episode = int(RE_EP.search(video_title).group(1))
            except: episode = 0
        else:
            episode = int(episode)
        if season==0:
            try: this_season = int(RE_SEASON.search(video_title).group(1))
            except:
                this_season = 0
        else:
            this_season = season
            
        if episode>0 or this_season>0:
            oc.add(EpisodeObject(url=new_url, title=video_title, season=this_season, index=episode, summary=desc, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image)))
        else:
            oc.add(VideoClipObject(url=new_url, title=video_title, summary=desc, originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=image)))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no videos that are currently available in this category right now.")
    else:
        return oc
#######################################################################################
# This function produces sections for specials
@route(PREFIX + '/specialsections')
def SpecialSections(title, url):
    oc = ObjectContainer(title2=title)
    current_url = url.replace('archive/', 'video.jhtml')
    oc.add(DirectoryObject(key=Callback(VideoPage, title="Current Year", url=current_url), title = "Current Year"))
    oc.add(DirectoryObject(key=Callback(SpecialArchives, title="Archives", url=url), title="Archives"))
    return oc
#######################################################################################
# This section separates the MTV specials with archives into years.
@route(PREFIX + '/specialarchives')
def SpecialArchives(title, url):

    oc = ObjectContainer(title2=title)
    # Pull the metadata for the current season
    data = HTML.ElementFromURL(url, cacheTime = CACHE_1DAY)
    thumb=data.xpath('//img[@id="featImg"]//@src')[0]
    if not thumb.startswith('http://'):
        thumb = BASE_URL + thumb
    for video in data.xpath('//li/p/b/a'):
        title = video.xpath('.//text()')[0]
        year = int(title.split()[0])
        # Chose to start at 2005 since that is the year that first seems to produce videos  
        if year > 2004:
            url = BASE_URL + video.xpath('.//@href')[0]
            # A few do not put slash after the year so it causes errors
            if not url.endswith('/'):
                url = url + '/'
            oc.add(DirectoryObject(key=Callback(ArchiveSections, title=title, url=url, thumb=thumb), title=title, thumb=thumb)) 

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no years list right now.")
    else:
        return oc
#######################################################################################
# This section handles the archived years of specials 
@route(PREFIX + '/archivesections')
def ArchiveSections(title, thumb, url):

    oc = ObjectContainer(title2=title)
    # Check to see if there is a second pages here
    data = HTML.ElementFromURL(url, cacheTime = CACHE_1HOUR)
    section_list =[]
    for videos in data.xpath('//div[@id="generic2"]//ol/li'):
        vid_id = videos.xpath('.//a//@href')[0].split('?id=')[1]
        title = videos.xpath('./p/strong/a//text()')[0]
        thumb = BASE_URL + videos.xpath('.//img//@src')[1]
        thumb = thumb.replace('70x53.jpg', '140x105.jpg')
        vid_url = BUILD_URL + vid_id
        oc.add(VideoClipObject(url=vid_url, title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))
	
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no special videos to list right now.")
    else:
        return oc
############################################################################################################################
# This function creates an error message for entries that are not currrently available
@route(PREFIX + '/notavailable')
def NotAvailable(avail):
  return ObjectContainer(header="Not Available", message='This video is currently unavailable - %s.' %avail)

