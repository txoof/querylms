# QueryLMS Python Library
QueryLMS manages queries to a Logitech Media Server and associates with a single player. A QueryLMS object can be used to query server or player status information and control an LMS player.

QueryLMS is a rewrite of [LMSQuery](https://github.com/roberteinhaus/lmsquery) and reuses a significant portion of the LMSQuery code.

Usage:
```
    import QueryLMS
    # create the object and try to discover LMS on the local network
    # try to associate with "My Player"
    my_player = QueryLMS(player_name='My Player')
    # get now playing tracks
    my_player.get_now_playing()
    >>> {'time': 0,
         'mode': 'stop',
         'id': 17001,
         'title': 'We Belong Together',
         'artist': 'Vampire Weekend feat. Danielle Haim',
         'coverid': 'c9d646ff',
         'duration': 190.733,
         'album_id': '2064',
         'genre': 'No Genre',
         'album': 'Father of the Bride',
         'artwork_url': 'http://192.168.178.9:9000/music/c9d646ff/cover.jpg'}
  
  # create the object with a defined hostname and port
  # try to associate with player "Living Room"
  living_room = QueryLMS(host="media-server.local", port=9001, player_name="Living Room")
  
```

## Changes

**V 0.2**

* add additional keys to `get_now_playing` method
* return now-playing information for streams 

Notes:

* Album artwork is not properly returned for streams
* Album information may not be returned at all for streams

## API

All player related calls will raise ValueError if player_id is not set.

```
class QueryLMS(builtins.object)
  QueryLMS(host=None, port=None, player_name=None, player_id=None, scan_timeout=1, handle_requests_exceptions=False, request_timeout=5)
  
  Class to handle queries for an LMS player
  
  Each Query LMS object is associated with a single player_id
  
  If no host and port number are specified, the QueryLMS object will attempt to locate
  an active LMS Server on the network. If a player_name is specified, the Query
  object will attempt to find the player_id associated with that name.
  
  All queries are run against the first located (or specified) 
  server or a single player.
  
  By default any http requests exceptions encoutered when communicating
  with the server are raised and should be handled by your program. 
  Suppress and log exceptions with handle_reqests_exceptions=True
  
  Attributes:
      host(str): LMS Server hostname or ip address
      port(int): LMS Server port number
      player_name(str): Player name
      player_id(str): unique player id in hex
      scan_timeout(int): seconds to search local network for an LMS server
      server_query_url(str): url to use when querying host status
      server_base_url(str): base url of server: http://host:port/
      handle_requests_exceptions(bool): True: quietly handle exceptions; False: raise exceptions
      request_timeout(int): seconds to wait for server to respond
      
  
  Additional API documentation: https://github.com/elParaguayo/LMS-CLI-Documentation/blob/master/LMS-CLI.md
  
  Methods defined here:
  
  __init__(self, host=None, port=None, player_name=None, player_id=None, scan_timeout=1, handle_requests_exceptions=False, request_timeout=5)
      inits QueryLMS Class with host, port, player_id, player_name and scan_timeout
      
      Args:
          host(str): LMS host name or ip address 
          port(int): LMS port number
          player_name(str): name of player to associate with
          player_id(str): player_id in hex 
          scan_timeout(int): seconds to search for LMS host
  
  display(self, line1, line2, duration=5)
      display line1 and line2 on associated player
      
      Args:
          line1(str)
          line1(str)
  
  display_all(self, line1, line2, duration=5)
      display line1 and line2 on all connected players
      
      Args:
          line1(str)
          line1(str)
  
  get_alarms(self, enabled=True)
      ???
  
  get_artist_album(self, artist_id)
      query associated player for currently playing album artist
      
      Returns:
          (str)
  
  get_artist_count(self)
      query server for total number of artists
      
      Returns:
          (int): count of unique artist ids
  
  get_artists(self)
      query server for internal artist id, names
      Returns:
          (dict): JSON formatted list of ids and artists
  
  get_current_album(self)
      query associated player for currently playing track album
      
      Returns:
          (str)
  
  get_current_artist(self)
      query associated player for currently playing artist
      
      Returns:
          (str)
  
  get_current_radio_title(self, radio)
      return title of favorite radio stations
  
  get_current_song_title(self)
      query associated player for currently playing track title
      
      Returns:
          (str)
  
  get_current_title(self)
      query associated player for currently playing track title
      
      Returns:
          (str)
  
  get_favorite_radio(self)
      return favorited radio stations
  
  get_next_alarm(self)
      ???
  
  get_now_playing(self)
      query associated player for now playing information including:
      * album
      * artist
      * artwork_url
      * duration
      * genre
      * coverid
      * id
      * title
      
      Returns:
          dict
  
  get_player_count(self)
      query server for total number of connected players
      
      Returns:
          (int): count of unique players connected
  
  get_player_pref(self, pref)
      ???
  
  get_players(self)
      query server for connected player information
      
      Returns:
          (dict): JSON formatted list of player information
  
  get_radios_count(self)
      query server for total number of saved radio stations
      
      Returns:
          (int): count of unique radios connected
  
  get_server_status(self)
      query server status in JSON
      
      Returns:
          (dict): JSON formatted server status
  
  get_volume(self)
      query associated player for volume
      
      Returns:
          (str)
  
  next_song(self)
      fast forward one track on associated player
      
      Returns:
          (dict): {}
  
  pause(self)
      pause associated player
      
      Returns:
          (dict): {}
  
  play_album(self, album_id)
      play an album on associated player
      
      Args:
          album_id(int): internal album id
          
      Returns:
          (dict): {'count': int} total tracks on album
  
  play_radio(self, radio)
      play radio??? on associated player

  play_stream(self, url)
      play compatible stream such as Internet Radio or sound file on associated player
  
  previous_song(self)
      rewind one track on associated player
      
      Returns:
          (dict): {}
  
  query(self, player_id=None, *args)
      # Basic Query
      #####################################
  
  rescan(self)
      rescan LMS library
      
      Returns:
          (dict): {}
  
  search(self, searchstring, count=9999)
      query server for searchstring (ignoring case)
      
      Args:
          searchstring(str): string to search for
      
      Returns:
          (dict): JSON formatted list of all entities containing searchstring
  
  search_albums(self, searchstring, count=9999)
      query server for searchstring in album names (ignoring case)
      
      Args:
          searchstring(str): string to search tracks for
          
      Returns:
          (dict): JSON formatted list of all album entities containing searchstring
  
  search_contributors(self, searchstring, count=9999)
      query server for searchstring in contributors names (ignoring case)
      
      Args:
          searchstring(str): string to search tracks for
          
      Returns:
          (dict): JSON formatted list of all contributors entities containing searchstring
  
  search_players(self, searchstring, count=9999)
      query server for searchstring in player names (ignoring case)
      
      Args:
          searchstring(str): string to search tracks for
          
      Returns:
          (dict): JSON formatted list of all player entities containing searchstring
  
  search_tracks(self, searchstring, count=9999)
      query server for searchstring in track names (ignoring case)
      
      Args:
          searchstring(str): string to search tracks for
          
      Returns:
          (dict): JSON formatted list of all track entities containing searchstring
  
  set_player_pref(self, pref, value)
      ???
  
  set_power(self, power=1)
      send power command to connected player
  
  set_power_all(self, power=1)
  
  set_server(self)
      set the server details using "host" and "port"
      
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
          player_id (if not already set)
  
  set_volume(self, volume)
      set volume on associated player
      
      Args:
          volume(int): 0-100
          
      Returns:
          (dict): {}
  
  skip_songs(self, amount=1)
      skip n tracks on associated player
      
      Args:
          amount(int): number of tracks to skip
      
      Returns:
          (dict): {}
  
  ----------------------------------------------------------------------
  Static methods defined here:
  
  scan_lms(scan_timeout=None)
      Search local network for Logitech Media Servers
      
      Based on netdisco/lms.py by cxlwill - https://github.com/cxlwill
      
      Args:
        scan_timeout (int): timeout seconds
      
      Returns:
        list: Dictionary of LMS Server IP and listen ports
  
  ----------------------------------------------------------------------
  Readonly properties defined here:
  
  is_playing_remote_stream
  
  ----------------------------------------------------------------------
  Data descriptors defined here:
  
  __dict__
      dictionary for instance variables (if defined)
  
  __weakref__
      list of weak references to the object (if defined)
  
  host
      LMS ip address or hostname: (str)
  
  player_id
      LMS player unique hexidecimal id (str)
  
  player_name
      human readable name of player: (str)
  
  port
      LMS server port: (int)

 ```
