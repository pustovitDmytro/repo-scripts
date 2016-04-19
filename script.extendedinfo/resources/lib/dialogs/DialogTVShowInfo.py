# -*- coding: utf8 -*-

# Copyright (C) 2015 - Philipp Temminghoff <phil65@kodi.tv>
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcgui
from .. import Utils
from .. import addon
from .. import ImageTools
from .. import TheMovieDB as tmdb
from DialogBaseInfo import DialogBaseInfo
from ..WindowManager import wm
from ActionHandler import ActionHandler
from ..VideoPlayer import PLAYER

ID_LIST_SIMILAR = 150
ID_LIST_SEASONS = 250
ID_LIST_NETWORKS = 1450
ID_LIST_STUDIOS = 550
ID_LIST_CERTS = 650
ID_LIST_CREW = 750
ID_LIST_GENRES = 850
ID_LIST_KEYWORDS = 950
ID_LIST_ACTORS = 1000
ID_LIST_VIDEOS = 1150
ID_LIST_IMAGES = 1250
ID_LIST_BACKDROPS = 1350

ID_BUTTON_BROWSE = 120
ID_BUTTON_PLOT = 132
ID_BUTTON_MANAGE = 445
ID_BUTTON_SETRATING = 6001
ID_BUTTON_OPENLIST = 6002
ID_BUTTON_FAV = 6003
ID_BUTTON_RATED = 6006

ch = ActionHandler()


def get_window(window_type):

    class DialogTVShowInfo(DialogBaseInfo, window_type):

        def __init__(self, *args, **kwargs):
            super(DialogTVShowInfo, self).__init__(*args, **kwargs)
            self.type = "TVShow"
            data = tmdb.extended_tvshow_info(tvshow_id=kwargs.get('tmdb_id', False),
                                             dbid=self.dbid)
            if not data:
                return None
            self.info, self.data, self.account_states = data
            if "dbid" not in self.info.get_properties():
                self.info.set_art("poster", Utils.get_file(self.info.get_art("poster")))
            self.info.update_properties(ImageTools.blur(self.info.get_art("poster")))
            self.listitems = [(ID_LIST_SIMILAR, self.data["similar"]),
                              (ID_LIST_SEASONS, self.data["seasons"]),
                              (ID_LIST_NETWORKS, self.data["networks"]),
                              (ID_LIST_STUDIOS, self.data["studios"]),
                              (ID_LIST_CERTS, tmdb.merge_with_cert_desc(self.data["certifications"], "tv")),
                              (ID_LIST_CREW, self.data["crew"]),
                              (ID_LIST_GENRES, self.data["genres"]),
                              (ID_LIST_KEYWORDS, self.data["keywords"]),
                              (ID_LIST_ACTORS, self.data["actors"]),
                              (ID_LIST_VIDEOS, self.data["videos"]),
                              (ID_LIST_IMAGES, self.data["images"]),
                              (ID_LIST_BACKDROPS, self.data["backdrops"])]

        def onInit(self):
            self.get_youtube_vids("%s tv" % (self.info.get_info("title")))
            super(DialogTVShowInfo, self).onInit()
            self.info.to_windowprops(window_id=self.window_id)
            super(DialogTVShowInfo, self).update_states()
            self.fill_lists()

        def onClick(self, control_id):
            super(DialogTVShowInfo, self).onClick(control_id)
            ch.serve(control_id, self)

        @ch.click(ID_BUTTON_BROWSE)
        def browse_tvshow(self):
            self.close()
            xbmc.executebuiltin("Dialog.Close(all)")
            xbmc.executebuiltin("ActivateWindow(videos,videodb://tvshows/titles/%s/)" % self.dbid)

        @ch.click(ID_LIST_CREW)
        @ch.click(ID_LIST_ACTORS)
        def credit_dialog(self):
            selection = xbmcgui.Dialog().select(heading=addon.LANG(32151),
                                                list=[addon.LANG(32009), addon.LANG(32147)])
            if selection == 0:
                wm.open_actor_info(prev_window=self,
                                   actor_id=self.listitem.getProperty("id"))
            if selection == 1:
                self.open_credit_dialog(self.listitem.getProperty("credit_id"))

        @ch.click(ID_LIST_SIMILAR)
        def open_tvshow_dialog(self):
            wm.open_tvshow_info(prev_window=self,
                                tmdb_id=self.listitem.getProperty("id"),
                                dbid=self.listitem.getProperty("dbid"))

        @ch.click(ID_LIST_SEASONS)
        def open_season_dialog(self):
            info = self.listitem.getVideoInfoTag()
            wm.open_season_info(prev_window=self,
                                tvshow_id=self.info.get_property("id"),
                                season=info.getSeason(),
                                tvshow=self.info.get_info("title"))

        @ch.click(ID_LIST_STUDIOS)
        def open_company_info(self):
            filters = [{"id": self.listitem.getProperty("id"),
                        "type": "with_companies",
                        "typelabel": addon.LANG(20388),
                        "label": self.listitem.getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters)

        @ch.click(ID_LIST_KEYWORDS)
        def open_keyword_info(self):
            filters = [{"id": self.listitem.getProperty("id"),
                        "type": "with_keywords",
                        "typelabel": addon.LANG(32114),
                        "label": self.listitem.getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters)

        @ch.click(ID_LIST_GENRES)
        def open_genre_info(self):
            filters = [{"id": self.listitem.getProperty("id"),
                        "type": "with_genres",
                        "typelabel": addon.LANG(135),
                        "label": self.listitem.getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters,
                               media_type="tv")

        @ch.click(ID_LIST_NETWORKS)
        def open_network_info(self):
            filters = [{"id": self.listitem.getProperty("id"),
                        "type": "with_networks",
                        "typelabel": addon.LANG(32152),
                        "label": self.listitem.getLabel().decode("utf-8")}]
            wm.open_video_list(prev_window=self,
                               filters=filters,
                               media_type="tv")

        @ch.click(ID_BUTTON_MANAGE)
        def show_manage_dialog(self):
            options = []
            title = self.info.get_info("tvshowtitle")
            if self.dbid:
                call = "RunScript(script.artwork.downloader,mediatype=tv,%s)"
                options += [[addon.LANG(413), call % ("mode=gui,dbid=" + self.dbid)],
                            [addon.LANG(14061), call % ("dbid=" + self.dbid)],
                            [addon.LANG(32101), call % ("mode=custom,dbid=" + self.dbid + ",extrathumbs")],
                            [addon.LANG(32100), call % ("mode=custom,dbid=" + self.dbid)]]
            else:
                options += [[addon.LANG(32166), "RunPlugin(plugin://plugin.video.sickrage?action=addshow&show_name=%s)" % title]]
            if xbmc.getCondVisibility("system.hasaddon(script.libraryeditor)") and self.dbid:
                options.append([addon.LANG(32103), "RunScript(script.libraryeditor,DBID=" + self.dbid + ")"])
            options.append([addon.LANG(1049), "Addon.OpenSettings(script.extendedinfo)"])
            selection = xbmcgui.Dialog().select(heading=addon.LANG(32133),
                                                list=[item[0] for item in options])
            if selection == -1:
                return None
            for item in options[selection][1].split("||"):
                xbmc.executebuiltin(item)

        @ch.click(ID_BUTTON_SETRATING)
        def set_rating(self):
            if tmdb.set_rating_prompt(media_type="tv",
                                      media_id=self.info.get_property("id"),
                                      dbid=self.info.get_property("dbid")):
                self.update_states()

        @ch.click(ID_BUTTON_OPENLIST)
        def open_list(self):
            index = xbmcgui.Dialog().select(heading=addon.LANG(32136),
                                            list=[addon.LANG(32144), addon.LANG(32145)])
            if index == 0:
                wm.open_video_list(prev_window=self,
                                   media_type="tv",
                                   mode="favorites")
            elif index == 1:
                wm.open_video_list(prev_window=self,
                                   mode="rating",
                                   media_type="tv")

        @ch.click(ID_BUTTON_FAV)
        def toggle_fav_status(self):
            tmdb.change_fav_status(media_id=self.info.get_property("id"),
                                   media_type="tv",
                                   status=str(not bool(self.account_states["favorite"])).lower())
            self.update_states()

        @ch.click(ID_BUTTON_RATED)
        def open_rated_items(self):
            wm.open_video_list(prev_window=self,
                               mode="rating",
                               media_type="tv")

        @ch.click(ID_BUTTON_PLOT)
        def open_text(self):
            xbmcgui.Dialog().textviewer(heading=addon.LANG(32037),
                                        text=self.info.get_info("plot"))

        @ch.click(ID_LIST_VIDEOS)
        def play_youtube_video(self):
            PLAYER.play_youtube_video(youtube_id=self.listitem.getProperty("youtube_id"),
                                      listitem=self.listitem,
                                      window=self)

        def update_states(self):
            xbmc.sleep(2000)  # delay because MovieDB takes some time to update
            _, __, self.account_states = tmdb.extended_tvshow_info(tvshow_id=self.info.get_property("id"),
                                                                   cache_time=0,
                                                                   dbid=self.dbid)
            super(DialogTVShowInfo, self).update_states()

    return DialogTVShowInfo