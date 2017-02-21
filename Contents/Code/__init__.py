# Copyright © 2013-2017 Valdas Vaitiekaitis

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Version 1.0.0

TITLE = 'IPTVLite'
PREFIX = '/video/iptvlite'

####################################################################################################
def Start():
    ObjectContainer.title1 = TITLE

####################################################################################################
@handler(PREFIX, TITLE)
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