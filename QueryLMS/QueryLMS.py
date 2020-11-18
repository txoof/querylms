#!/usr/bin/env python3
# coding: utf-8






import requests
import socket
import json

try:
    from . import constants
except ImportError as e:
    import constants

import logging






logger = logging.getLogger(__name__)






class QueryLMS():
    '''Class to handle queries for an LMS player
    
    Each Query LMS object is associated with a single player_id
    
    If no host and port number are specified, the QueryLMS object will attempt to locate
    an active LMS Server on the network. If a player_name is specified, the Query
    object will attempt to find the player_id associated with that name.
    
    All queries are run against the first located (or specified) 
    server or a single player.
    
    By default any http requests exceptions encoutered when communicating
    with the server are raised and should be handled by your program. 
    Supress and log exceptions with handle_reqests_exceptions=True
    
    Attributes:
        host(str): LMS Server hostname or ip address
        port(int): LMS Server port number
        player_name(str): Player name
        player_id(str): unique player id in hex
        scan_timeout(int): seconds to search local network for an LMS server
        server_query_url(str): url to use when querying host status
        server_base_url(str): base url of server: http://host:port/
        handle_requests_exceptions(bool): True: quietly handle exceptions; False: raise exceptions
        
    
        '''
    def __init__(self, host=None, port=None, 
                 player_name=None, 
                 player_id=None, 
                 scan_timeout=5,
                 handle_requests_exceptions=False):
        '''inits QueryLMS Class with host, port, player_id, player_name and scan_timeout
        
        Args:
            host(str): LMS host name or ip address 
            port(int): LMS port number
            player_name(str): name of player to associate with
            player_id(str): player_id in hex 
            scan_timeout(int): seconds to search for LMS host
        '''
        self.handle_requests_exceptions=handle_requests_exceptions
        self.host = host
        self.port = port        
        self.player_id = player_id
        self.player_name = player_name
        self.scan_timeout = scan_timeout
        self.set_server()
        
    
    @property
    def host(self):
        '''LMS ip address or hostname: (str)'''
        return self._host
    
    @host.setter
    def host(self, host):
        self._host = host
    
    @property
    def port(self):
        '''LMS server port: (int)'''
        return self._port

    @port.setter
    def port(self, port):
        self._port = port
        
    @property
    def player_name(self):
        '''human readable name of player: (str)'''
        return self._player_name
    
    @player_name.setter
    def player_name(self, player_name):
        self._player_name = player_name
#         if player_name and not self.player_id:
#             player_id = None
#             logging.info(f'attempting to locate player_id for {player_name}')
#             for p in self.get_players():
#                 if 'name' in p and 'playerid' in p:
#                     if p['name'] == player_name:
#                         player_id = p['playerid']
            
#             self.player_id = player_id
                

    @property
    def player_id(self):
        '''LMS player unique hexidecimal id (str)'''
        return self._player_id
    
    @player_id.setter
    def player_id(self, player_id):
        self._player_id = player_id
            

    def _check_attribute(self, attribute, check_value=True, invalid_values=[], exception=AttributeError):
        if hasattr(self, attribute):
            my_attribute = getattr(self, attribute)
            if check_value:
                for value in invalid_values:
                    if my_attribute == value:
                        raise ValueError(f'invalid value "{value}" for "{attribute}"')
            else:
                pass
        else:
            raise exception()
        
    def set_server(self):
        '''set the server details using "host" and "port"
        
        If no host and port is specified, queryLMS will search for the 
        first LMS server on the local network segment.
        
        If the server IP/name or port change it is necessary
        to run set_server() again to trigger updates of the query urls
        
        QueryLMS will not detect dynamic changes of player name.
        
        Use the static method scan_lms() to find host information
        
        Use the get_players() method to list player names/ids associated with a LMS
        
        Sets:
            server_query_url
            server_base_url
            player_id (if not already set)'''
        
        base_url = None
        query_url = None

        
        if self.host and self.port:
            my_host = self.host
            my_port = self.port
        else:
            my_host = None
            my_port = None

            server_list = self.scan_lms(self.scan_timeout)
            if server_list:
                try:
                    my_host = server_list[0]['host']
                    my_port = server_list[0]['port']
                except (KeyError, IndexError) as e:
                    logging.warning(f'server search returned no valid data: {e}; is there an LMS on the local network?')

            self.host = my_host
            self.port = my_port

        if my_host and my_port:
            base_url = constants.LMS_QUERY_BASE_URL.format(self.host, self.port)
            query_url = constants.LMS_QUERY_ENDPOINT.format(base_url)
                    
#         self.lms_server = {'host': my_host, 'port': my_port}          
        self.server_base_url = base_url
        self.server_query_url = query_url
        
        if self.player_name and not self.player_id:
            player_id = None
#             logging.info(f'attempting to locate player_id for {player_name}')
            for p in self.get_players():
                if 'name' in p and 'playerid' in p:
                    if p['name'] == self.player_name:
                        player_id = p['playerid']
                        break
            
            self.player_id = player_id
        

    
    @staticmethod
    def scan_lms(scan_timeout=None):
        '''Search local network for Logitech Media Servers

        Based on netdisco/lms.py by cxlwill - https://github.com/cxlwill

        Args:
          scan_timeout (int): timeout seconds

        Returns:
          list: Dictionary of LMS Server IP and listen ports

        '''
        lmsIP  = '<broadcast>'
        lmsPort = constants.LMS_BRDCST_PORT
        lmsMsg = constants.LMS_BRDCST_MSG
        # search for servers unitl timeout expires
        if scan_timeout:
            lmsTimeout = scan_timeout
        else:
            lmsTimeout = constants.LMS_BRDCST_TIMEOUT

        entries = []

        mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        mySocket.settimeout(lmsTimeout)
        mySocket.bind(('', 0))
        logging.info(f'searching for LMS servers for {lmsTimeout} seconds')
        try:
            mySocket.sendto(lmsMsg, (lmsIP, lmsPort))
            while True: # loop until the timeout expires
                try:
                    data, address = mySocket.recvfrom(1024) # read 1024 bytes from the socket
                    if data and address:
                        port = None
                        if data.startswith(b'EJSON'):
                            position = data.find(b'N')
                            length = int(data[position+1:position+2].hex())
                            port = int(data[position+2:position+2+length])
                            entries.append({'host': address[0], 'port': port})

                except socket.timeout:
                    if len(entries) < 1:
                        logging.warning(f'server search timed out after {lmsTimeout} seconds with no results')
                    break            
                except OSError as e:
                    logging.error(f'error opening socket: {e}')
        finally:
            mySocket.close()
        return entries   
        

    # Basic Query
    #####################################
    def query(self, player_id="", *args):
        r = {}
        retval = {}
        params = json.dumps({'id': 1, 'method': 'slim.request',
                             'params': [player_id, list(args)]})
        if self.server_query_url:
            try:
                r = requests.post(self.server_query_url, params)
            except requests.exceptions.RequestException as e:
                if self.handle_requests_exceptions:
                    logging.warning(f'error making connection to server: {e}')
                else:
                    raise e
            if r:
                retval = json.loads(r.text)['result']
        else:
            logging.warning('"server_query_url" is not set')

        return retval

    # Server commands
    #####################################
    def rescan(self):
        '''rescan LMS library
        
        Returns:
            (dict): {}'''
        return self.query("", "rescan")
    
    def get_server_status(self):
        '''query server status in JSON
        
        Returns:
            (dict): JSON formatted server status'''
        return self.query("", "serverstatus", 0, 99)

    def get_artists(self):
        '''query server for internal artist id, names
        Returns:
            (dict): JSON formatted list of ids and artists'''
        return self.query("", "artists", 0, 9999)['artists_loop']

    def get_artist_count(self):
        '''query server for total number of artists
        
        Returns:
            (int): count of unique artist ids'''
        return len(self.get_artists())

    def get_radios_count(self):
        '''query server for total number of radios
        
        Returns:
            (int): count of unique radios connected'''
        return self.query("", "favorites", "items")['count']

    def get_player_count(self):
        '''query server for total number of connected players
        
        Returns:
            (int): count of unique players connected'''
        return self.query("", "player", "count", "?")['_count']    
    
    def get_players(self):
        '''query server for connected player information
        
        Returns:
            (dict): JSON formatted list of player information'''
        players = self.get_server_status()
        if len(players):
            players = players['players_loop']
        return players
    
    def search(self, searchstring, count=9999):
        '''query server for searchstring (ignoring case)
        
        Args:
            searchstring(str): string to search for
        
        Returns:
            (dict): JSON formatted list of all entities containing searchstring
            '''
        return self.query('', "search", 0, count, "term:" + searchstring)

    def search_tracks(self, searchstring, count=9999):
        '''query server for searchstring in track names (ignoring case)
        
        Args:
            searchstring(str): string to search tracks for
            
        Returns:
            (dict): JSON formatted list of all track entities containing searchstring'''
        result = self.search(searchstring, count)
        if 'tracks_loop' in result:
            response = {"tracks_count": result['tracks_count'],
                    "tracks_loop": result['tracks_loop']}
        else:
            response = {"tracks_count": 0}
        return response

    def search_albums(self, searchstring, count=9999):
        '''query server for searchstring in album names (ignoring case)
        
        Args:
            searchstring(str): string to search tracks for
            
        Returns:
            (dict): JSON formatted list of all album entities containing searchstring'''        
        result = self.search(searchstring, count)
        if 'albums_loop' in result:
            response = {"albums_count": result['albums_count'],
                    "albums_loop": result['albums_loop']}
        else:
            response = {"albums_count": 0}
        return response

    def search_contributors(self, searchstring, count=9999):
        '''query server for searchstring in contributors names (ignoring case)
        
        Args:
            searchstring(str): string to search tracks for
            
        Returns:
            (dict): JSON formatted list of all contributors entities containing searchstring'''        
        result = self.search(searchstring, count)
        if 'contributors_loop' in result:
            response = {"contributors_count": result['contributors_count'],
                    "contributors_loop": result['contributors_loop']}
        else:
            response = {"contributors_count": 0}
        return response

    def search_players(self, searchstring, count=9999):
        '''query server for searchstring in player names (ignoring case)
        
        Args:
            searchstring(str): string to search tracks for
            
        Returns:
            (dict): JSON formatted list of all player entities containing searchstring'''        
        players = self.get_players()
        result = []
        count = 0
        for player in players:
            for value in list(player.values()):
                if(searchstring.lower() in str(value).lower()):
                    result.append(player)
                    count = count + 1
        if count > 0:
            response = {"players_count": count, "players_loop": result}
        else:
            response = {"players_count": count}
        return response

    def set_power(self, power=1):
        '''send power command to connected player'''
        self.query(self.player_id, "power", power)

    def set_power_all(self, power=1):
        players = self.get_players()
        for player in players:
            self.set_power(player['playerid'], power)

    # Player Commands
    #####################################    
    def play_album(self, album_id):
        '''play an album on associated player
        
        Args:
            album_id(int): internal album id
            
        Returns:
            (dict): {'count': int} total tracks on album'''
        self._check_attribute(attribute='player_id', 
                      check_value=True, 
                      invalid_values=[None, ''])

        return self.query(self.player_id, "playlistcontrol", "cmd:load",
                          "album_id:" + str(album_id))

    def play_radio(self, radio):
        '''play radio??? on associated player'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        return self.query(self.player_id, "favorites", "playlist", "play",
                          "item_id:" + str(radio))

    def pause(self):
        '''pause associated player
        
        Returns:
            (dict): {}'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        return self.query(self.player_id, "pause")

    def skip_songs(self, amount=1):
        '''skip n tracks on associated player
        
        Args:
            amount(int): number of tracks to skip
        
        Returns:
            (dict): {}'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])

        if amount > 0:
            amount = "+" + str(amount)
        else:
            amount = str(amount)
        return self.query(self.player_id, "playlist", "index", amount)

    def previous_song(self):
        '''rewind one track on associated player
        
        Returns:
            (dict): {}'''
        self._check_attribute(attribute='player_id', 
                          check_value=True, 
                          invalid_values=[None, ''])

        return self.skip_songs(-1)

    def next_song(self):
        '''fast forward one track on associated player
        
        Returns:
            (dict): {}'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        return self.skip_songs()
    
    def get_volume(self):
        '''query associated player for volume
        
        Returns:
            (str)'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        volume = self.query(self.player_id, "mixer", "volume", "?")
        if len(volume):
            volume = volume['_volume']
        else:
            volume = 0            
        return volume

    def set_volume(self, volume):
        '''set volume on associated player
        
        Args:
            volume(int): 0-100
            
        Returns:
            (dict): {}'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        return self.query(self.player_id, "mixer", "volume", volume)
        

    def get_current_song_title(self):
        '''query associated player for currently playing track title
        
        Returns:
            (str)'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        title = self.query(self.player_id, "current_title", "?")
        if len(title):
            title = title['_current_title']
        else:
            title = ""
        return title

    def get_current_artist(self):
        '''query associated player for currently playing artist
        
        Returns:
            (str)'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])

        artist = self.query(self.player_id, "artist", "?")
        if len(artist):
            artist = artist['_artist']
        else:
            artist = ""
        return artist

    def get_current_album(self):
        '''query associated player for currently playing track album
        
        Returns:
            (str)'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        album = self.query(self.player_id, "album", "?")
        if len(album):
            album = album['_album']
        else:
            album = ""
        return album

    def get_current_title(self):
        '''query associated player for currently playing track title
        
        Returns:
            (str)'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        title = self.query(self.player_id, "title", "?")
        if len(title):
            title = title['_title']
        else:
            title = ""
        return title

    def get_current_radio_title(self, radio):
        '''???'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        return self.query(self.player_id, "favorites",
                          "items", 0, 99)['loop_loop'][radio]['name']

    def is_playing_remote_stream(self):
        '''???'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        return self.query(self.player_id, "remote", "?")['_remote'] == 1

    def get_artist_album(self, artist_id):
        '''query associated player for currently playing album artist
        
        Returns:
            (str)'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        return self.query(self.player_id, "albums", 0, 99, "tags:al",
                          "artist_id:" + str(artist_id))['albums_loop']

    def get_alarms(self, enabled=True):
        '''???'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        if enabled:
            alarmsEnabled = self.get_player_pref(self.player_id, "alarmsEnabled")
            if alarmsEnabled == "0":
                return {}
            alarm_filter = "enabled"
        else:
            alarm_filter = "all"
        return self.query(self.player_id, "alarms", 0, 99,
            "filter:%s" % alarm_filter)

    def get_next_alarm(self):
        '''???'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        alarms = self.get_alarms(self.player_id)
        alarmtime = 0
        delta = 0
        if alarms == {} or alarms['count'] == 0:
            return {}
        for alarmitem in alarms['alarms_loop']:
            if(str((datetime.datetime.today().weekday() + 1) % 7)
               not in alarmitem['dow']):
                continue
            alarmtime_new = datetime.timedelta(seconds=int(alarmitem['time']))
            now = datetime.datetime.now()
            currenttime = datetime.timedelta(hours=now.hour,
                                             minutes=now.minute,
                                             seconds=now.second)
            delta_new = alarmtime_new - currenttime
            if delta == 0:
                delta = delta_new
                alarmtime = alarmtime_new
            elif delta_new < delta:
                delta = delta_new
                alarmtime = alarmtime_new
        if alarmtime == 0:
            return {}
        else:
            return {"alarmtime": alarmtime.seconds, "delta": delta.seconds}

    def get_now_playing(self):
        '''query associated player for now playing information including:
        * album
        * artist
        * artwork_url
        * duration
        * genre
        * coverid
        * id
        * title'''  
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        status_keys = ['time', 'mode']
        
        status = self.query(self.player_id, 'status')
        track_id = None
        song_info = None
        now_playing_info = {}
        
        if status:
            try:
                playing_track = self.query(self.player_id, 'status', 
                                           int(status['playlist_cur_index']), 1, '-')['playlist_loop'][0]
                track_id = playing_track['id']
                song_info = self.query('', 'songinfo', 0, 100, 'track_id:'+str(track_id), 'tags:a,c,d,e,g,l')['songinfo_loop']
                for key in status_keys:
                    if key in status:
                        now_playing_info[key] = status[key]
                    else:
                        now_playing_info[key] = None
            except (KeyError, IndexError):
                pass
       
        if song_info:
            try:
                for each in song_info:
                    for key in each:
                        now_playing_info[key] = each[key]
                coverid = 0
                if 'coverid' in now_playing_info:
                    if now_playing_info['coverid'].startswith('-'):
                        pass
                    else:
                        coverid = now_playing_info['coverid']
                now_playing_info['artwork_url'] = f'{self.server_base_url}music/{coverid}/cover.jpg'
            except (KeyError, IndexError):
                pass
            

        return now_playing_info
    
    def get_player_pref(self, pref):
        '''???'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        return self.query(self.player_id, "playerpref", pref, "?")['_p2']

    def set_player_pref(self, pref, value):
        '''???'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        self.query(self.player_id, "playerpref", pref, value)

    def display(self, line1, line2, duration=5):
        '''display line1 and line2 on associated player
        
        Args:
            line1(str)
            line1(str)'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])
        
        self.query(self.player_id, "display", line1, line2, duration)

    def display_all(self, line1, line2, duration=5):
        '''display line1 and line2 on all connected players
        
        Args:
            line1(str)
            line1(str)'''
        self._check_attribute(attribute='player_id', 
                              check_value=True, 
                              invalid_values=[None, ''])

        players = self.get_players()
        for player in players:
            self.display(player['playerid'], line1, line2, duration)











