NAME = 'IPTVLite'
PREFIX = '/video/iptvlite'

####################################################################################################
def Start():
    ObjectContainer.title1 = NAME

####################################################################################################
@handler(PREFIX, NAME)
def MainMenu():
    oc = ObjectContainer()
    playlist = Resource.Load('playlist.m3u', binary = True)
    if playlist:
        lines = playlist.splitlines()
        for i in range(len(lines) - 1):
            line = lines[i].strip()
            if line.startswith('#EXTINF'):
                url = lines[i + 1].strip()
                if url.startswith('#EXTVLCOPT') and i + 1 < len(lines):
                    # skip VLC specific run-time options
                    i = i + 1
                    url = lines[i + 1].strip()
                if url and not url.startswith('#'):
                    title = line[line.rfind(',') + 1:len(line)].strip()
                    oc.add(
                        CreateVideoClipObject(
                            url = url,
                            title = title
                        )
                    )
                    i = i + 1 # skip the url line for the next cycle
    if len(oc) > 0:
        return oc
    else:
        return ObjectContainer(header = "Error", message = "File playlist.m3u is invalid or missing")

####################################################################################################
@route(PREFIX + '/createvideoclipobject', include_container = bool)
def CreateVideoClipObject(url, title, include_container = False, **kwargs):
    vco = VideoClipObject(
        key = Callback(CreateVideoClipObject, url = url, title = title, include_container = True),
        rating_key = url,
        title = title,
        items = [
            MediaObject(
                parts = [
                    PartObject(
                        key = Callback(PlayVideo, url = url)
                    )
                ],
            )
        ]
    )
    if include_container:
        return ObjectContainer(objects = [vco])
    else:
        return vco

####################################################################################################
@route(PREFIX + '/playvideo')
@indirect
def PlayVideo(url):
	return IndirectResponse(VideoClipObject, key = url)