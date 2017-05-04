# Simplified version of Plex plug-in that plays live streams (like IPTV) from a M3U playlist

# Copyright © 2013-2017 Valdas Vaitiekaitis

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Version 1.0.1

NAME = 'IPTVLite'
PREFIX = '/video/' + NAME.lower()

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
        line_count = len(lines)
        for i in range(line_count - 1):
            line_1 = lines[i].strip()
            if line_1.startswith('#EXTINF'):
                title = unicode(line_1[line_1.rfind(',') + 1:len(line_1)].strip())
                url = None
                for j in range(i + 1, line_count):
                    line_2 = lines[j].strip()
                    if line_2:
                        if not line_2.startswith('#'):
                            url = line_2
                            i = j + 1
                            break
                if url:
                    oc.add(
                        CreateVideoClipObject(
                            url = url,
                            title = title
                        )
                    )
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
                        key = HTTPLiveStreamURL(Callback(PlayVideo, url = url))
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
@indirect
@route(PREFIX + '/playvideo.m3u8')
def PlayVideo(url):

	return IndirectResponse(VideoClipObject, key = url)