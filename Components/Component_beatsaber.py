import twitchio
from twitchio import eventsub
from twitchio.ext import commands
import asyncio

import os

from .beatsaber.bsdatapuller_tools import BSDataListener
from .beatsaber import bs_tools as bst
# from beatsaber import bs_tools as bst # for debug only

import datetime


conf_path = r'./Components/beatsaber/bsr_conf.json'
minimal_follow_time = 60

async def get_viewer_following_time(chatter:twitchio.Chatter):
    follow_info = await chatter.follow_info()
    if follow_info is None:
        return 0
    else:
        # check if follow_inf as attribute followed_at
        if hasattr(follow_info, "followed_at"):
            followed_at = follow_info.followed_at
            follow_time = datetime.datetime.now()-followed_at
            follow_time = follow_time.total_seconds()
        else:
            follow_time = 0
    return follow_time

class BeatsaberComponent(commands.Component):
    # An example of a Component with some simple commands and listeners
    # You can use Components within modules for a more organized codebase and hot-reloading.

    def __init__(self,) -> None: # bot: Bot
        # Passing args is not required...
        # We pass bot here as an example...
        # self.bot = bot
        pass

    def is_meetting_condition():
        async def predicate(ctx: commands.Context) -> bool:
            
            if (ctx.chatter.broadcaster 
                or ctx.chatter.moderator
                ):
                return True
            
            follow_time = get_viewer_following_time(ctx.chatter)
            
            if follow_time < minimal_follow_time:
                return False

            return True

        return commands.guard(predicate)

    # An example of listening to an event
    # We use a listener in our Component to display the messages received.
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")

    @commands.command()
    async def request(self, ctx: commands.Context) -> None:
        """Command that lists available commands for Beatsaber
        """
        message= f''' 
        To request tracks, just send '!bsr key_of_the_track'
        You can find keys on https://beatsaver.com
        You need to follow for at least {minimal_follow_time}s to request
        Tracks need to meet channels rules and some minimal requirement
        '''
        await ctx.reply(f"Hi {ctx.chatter.mention}, {message}")

    # @is_meetting_condition()
    @commands.command()
    async def bsr(self, ctx: commands.Context, *, message: str) -> None:
        """add song based on bsr key
        """
        try:
            passed_check,log = await playlist.add_song_to_list(message,
                                                         requester=ctx.chatter
                                                         )
        except Exception as e:
            passed_check = False
            log = f"  Error while adding tracks: {e}"


        await ctx.send(ctx.chatter.mention+': '+ log)

    @commands.command()
    async def queue(self, ctx: commands.Context) -> None:
        """Display upcoming tracks in the queue
        """
        log = playlist.get_playlist_list(include_future=True)


        await ctx.send(ctx.chatter.mention+': '+ log)


    @commands.is_elevated()
    @commands.command(aliases=['bs'])
    async def bsr_ctrl(self, ctx: commands.Context, *, message: str) -> None:
        """Command to control bsr playlists with command !bsr_ctrl
        """
        match message:
            case 'open':
                playlist.is_open = True
                await ctx.send('Beatsaber playlist is open')
            case 'close':
                playlist.is_open = False
                await ctx.send('Beatsaber playlist is closed')
            case 'next':
                current_song = playlist.change_index(1)
                await ctx.send(f'Current song is {current_song.get('songName', '')} requested by {current_song.get('requester', '')}')
            case 'previous':
                current_song = playlist.change_index(-1)
                await ctx.send(f'Current song is {current_song.get('songName', '')} requested by {current_song.get('requester', '')}')
            case s if s.startswith('remove'):
                ''' remove based on index '''
                pass
            case s if s.startswith('move'):
                ''' remove based on index to index'''
                pass
            case s if s.startswith('extend'):
                ''' add slot in the queue'''
                try:
                    str_int = s.replace('extend','')
                    offset = int(str_int)
                    playlist.queue_limit += offset
                    await ctx.send(f'Beatsaber playlist limit is now {playlist.queue_limit}')
                except:
                    pass
            case s if s.startswith('clear'):
                playlist.reinitialize_playlist()
                await ctx.send('Beatsaber playlist cleared')
            case s if s.startswith('max_request'):
                try:
                    message.replace('max_request','')
                    offset = int(message)
                    playlist.queue_limit += offset
                    await ctx.send(f'Max request per viewer limit is now {playlist.queue_limit}')
                except:
                    pass
            case s:
                pass


class BeatSaberPlaylist():

    def __init__(self, add_data_listener=False):
        conf = bst.load_json_as_dic(conf_path)
        self.playlist_path: str = conf.get("CUSTOM_PLAYLIST_PATH")
        self.obs_txt_path: str = conf.get("OBS_REQUEST_TXT_PATH")
        self.is_open = False
        self.queue_limit: str = conf.get("PLAYLIST_MAX_SIZE")
        self.max_request_per_follower: str = conf.get("MAX_REQUEST_PER_FOLLOWER")
        self.max_request_per_viewer: str = conf.get("MAX_REQUEST_PER_VIEWER")
        self.request_conditions = conf.get("request_condition")
        self.current_index = 0
        if add_data_listener:
            self.data_listener = BSDataListener(playlist = self)
            asyncio.run(self.data_listener.main())


        
        pass

    async def add_song_to_list(self, key:str, requester : twitchio.Chatter) -> None:

        file_path = self.playlist_path

        current_song_list = bst.get_songs_from_bplist(file_path)

        if len(current_song_list) >= int(self.queue_limit):
            return False, 'Playlist is full.'
        elif not self.is_open:
            return False, 'Playlist is closed.'
        elif len(key)>5 or len(key)<4:
            return False, 'This key is not valid'
        else:   
            count = 0
            for i,s in enumerate(current_song_list):
                if requester and s.get('requester','')==requester.display_name:
                    count += 1
                if s.get('key') == key:
                    if i>self.current_index:
                        return False, 'This track is already in the queue'
                    else:
                        return False, 'This track has already been played'
        # check for already submitted song by this user
        if requester and (
            # not requester.moderator and 
            not requester.subscriber and 
            not requester.broadcaster):

            follow_time = await get_viewer_following_time(requester)

            if follow_time>0 and self.max_request_per_follower:
                return False, f'max request per follower is {self.max_request_per_follower}'
            elif count >= self.max_request_per_viewer:
                return False, f'max request per non following viewer is {self.max_request_per_viewer}'
        
        info = bst.get_song_info_by_id(key)
        if info is None:
            return False, f'this key do not exist: {key}'

        passed_check,log = bst.check_song_conditions(info,conditions=self.request_conditions)
        if passed_check:
            try:
                bst.add_song_to_bplist(file_path,info, 
                                       requester_name=requester.display_name
                                       )
            except Exception as e:
                log += f"\n Failed to add {key}. Reason: {e}"
                passed_check = False

        if passed_check:
            try:
                song_name = info.get('name',key)
                
                log = f"\n {song_name} was added to the playlist at position{len(current_song_list)}."
                self.actualize_obs_queue()
            except Exception as e:
                log += f"\n Failed to update the overlay. Reason: {e}"
            
            
        else:
            log += f"\n Failed to add {key} to the playlist"

        return passed_check,log
    

    def change_index(self,offset):
        self.current_index = max(self.current_index+offset,0)
        self.actualize_obs_queue()
        return self.get_song_at_index(self.current_index)

    def set_song_from_datapuller(self,data):
        s_list = bst.get_songs_from_bplist(self.playlist_path)
        for i,s in enumerate(s_list):
            if s.get('hash','') == data.get('Hash'):
                self.current_index = i
                self.actualize_obs_queue()
                return True
        
        print('current sound is out of playlist')               

        pass

    def reinitialize_playlist(self) -> None:
        bst.clear_songs_from_bplist(self.playlist_path)
        self.current_index = 0
        self.actualize_obs_queue()
        pass


    def get_song_at_index(self,index:int)->dict|None:
        try:
            return bst.get_songs_from_bplist(self.playlist_path)[index]
        except Exception as e:
            return {}

    def actualize_obs_queue(self,
                            keys = ['songName','requester'],
                            indexes=[-1,0,1]) -> None:
        current_song_list = bst.get_songs_from_bplist(self.playlist_path)


        for i in indexes:
            ind = self.current_index+i
            for k in keys:
                text = ''
                if ind >= 0 and ind<len(current_song_list):
                    text = current_song_list[ind].get(k,'')
                bst.write_obs_txt(self.obs_txt_path+f"track_{str(i)}_{k}.txt", text)  


    def get_playlist_list(self,
                          include_past=False,
                          include_current=False,
                          include_future=False)->str:
        song_list = bst.get_songs_from_bplist(self.playlist_path)
        log = f'''Playlist length: {len(song_list)}/{self.queue_limit}                        
                Current index: {self.current_index}\n
                '''

        for i,song in enumerate(song_list):
            if include_past and i<self.current_index:
                if i==0:
                    log+='Already played:\n'
                log+=f'''{i} - {song['songName']} requested by {song['requester']}
                '''
            if include_current and i==self.current_index:
                log+=f'''Current song:\n{song['songName']} requested by {song['requester']}
               '''
            if include_future and i>self.current_index:
                if i==self.current_index+1:
                    log+='To come:\n'''
                log+=f'''{i} - {song['songName']} requested by {song['requester']}
                '''
        return log
    
    # def save_datapuller_mapinfo_as_txt(self,data,to_get=["SongName","SongAuthor","Mapper","Difficulty","BPM","NJS"]):
    #     for k in to_get:
    #         info = data.get(k)
    #         bst.write_obs_txt(self.obs_txt_path+f"currentTrack_{k}.txt",info)


    #     pass












playlist = BeatSaberPlaylist(add_data_listener=True)

if __name__ == "__main__":
    # playlist.reinitialize_playlist()
    playlist.add_song_to_list('d1cc',requester=None)
    
