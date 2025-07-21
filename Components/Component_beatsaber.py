import twitchio
from twitchio import eventsub
from twitchio.ext import commands
import random

import os
from .beatsaber import bs_tools as bst
from dotenv import load_dotenv
import datetime


load_dotenv(r'./Components/beatsaber/bsr.env')
minimal_follow_time = 60




class BeatsaberComponent(commands.Component):
    # An example of a Component with some simple commands and listeners
    # You can use Components within modules for a more organized codebase and hot-reloading.

    def __init__(self,) -> None: # bot: Bot
        # Passing args is not required...
        # We pass bot here as an example...
        # self.bot = bot
        pass

    def is_meetting_condition():
        def predicate(ctx: commands.Context) -> bool:
            follow_info = ctx.chatter.follow_info()
            if follow_info is None:
                return False
            else:
                followed_at = follow_info.followed_at
                follow_time = datetime.datetime.now()-followed_at
            
            if follow_time.total_seconds()<minimal_follow_time:
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
        You need to follow for at least {minimal_follow_time} to request
        Tracks need to meet channels requirement
        '''
        await ctx.reply(f"Hi {ctx.chatter}, {message}")

    @is_meetting_condition()
    @commands.command()
    async def bsr(self, ctx: commands.Context, *, message: str) -> None:
        """user ask for a song to be added on the list:
                playlist fit playlist condition
                    user fit user condition
                        request fit sound condition
                            sound is added to playlist with user id
                            sound is added to beatsaber custom playlist
                        release:
                            send message with explaination
                    explain condition to user:
                        "you need to follow the channel for request"
                else:
                    explain why playlist is closed
        """
        try:
            passed_check,log = playlist.add_song_to_list(message,
                                                         requester=ctx.chatter
                                                         )
        except Exception as e:
            passed_check = False
            log = f"  Error while adding tracks: {e}"


        await ctx.send(log)


    @commands.is_elevated()
    @commands.command()
    async def bsr_ctrl(self, ctx: commands.Context, *, message: str) -> None:
        """Command to control bsr playlists with command !bsr_ctrl
        """
        match message:
            case 'next':
                playlist.change_index(1)
            case 'previous':
                playlist.change_index(-1)
            case s if s.startswith('remove'):
                ''' remove based on index '''
                pass
            case s if s.startswith('move'):
                ''' remove based on index to index'''
                pass
            case s if s.startswith('extend'):
                ''' add slot in the queue'''
                try:
                    message.replace('extend','')
                    offset = int(message)
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



        

    # @commands.command()
    # async def add(self, ctx: commands.Context, left: int, right: int) -> None:
    #     """Command which adds to integers together.

    #     !add <number> <number>
    #     """
    #     await ctx.reply(f"{left} + {right} = {left + right}")

    # @commands.command()
    # async def choice(self, ctx: commands.Context, *choices: str) -> None:
    #     """Command which takes in an arbitrary amount of choices and randomly chooses one.

    #     !choice <choice_1> <choice_2> <choice_3> ...
    #     """
    #     await ctx.reply(f"You provided {len(choices)} choices, I choose: {random.choice(choices)}")

    # @commands.command(aliases=["thanks", "thank"])
    # async def give(self, ctx: commands.Context, user: twitchio.User, amount: int, *, message: str | None = None) -> None:
    #     """A more advanced example of a command which has makes use of the powerful argument parsing, argument converters and
    #     aliases.

    #     The first argument will be attempted to be converted to a User.
    #     The second argument will be converted to an integer if possible.
    #     The third argument is optional and will consume the reast of the message.

    #     !give <@user|user_name> <number> [message]
    #     !thank <@user|user_name> <number> [message]
    #     !thanks <@user|user_name> <number> [message]
    #     """
    #     msg = f"with message: {message}" if message else ""
    #     await ctx.send(f"{ctx.chatter.mention} gave {amount} thanks to {user.mention} {msg}")

    # @commands.group(invoke_fallback=True)
    # async def socials(self, ctx: commands.Context) -> None:
    #     """Group command for our social links.

    #     !socials
    #     """
    #     await ctx.send("discord.gg/..., youtube.com/..., twitch.tv/...")

    # @socials.command(name="discord")
    # async def socials_discord(self, ctx: commands.Context) -> None:
    #     """Sub command of socials that sends only our discord invite.

    #     !socials discord
    #     """
    #     await ctx.send("discord.gg/...")



class BeatSaberPlaylist():

    def __init__(self):
        self.playlist_path: str = os.getenv("CUSTOM_PLAYLIST_PATH")
        self.obs_txt_path: str = os.getenv("OBS_REQUEST_TXT_PATH")
        self.is_open = False
        self.queue_limit: str = os.getenv("PLAYLIST_MAX_SIZE")
        self.max_request_per_viewer: str = os.getenv("MAX_REQUEST_PER_FOLLOWER")
        request_conditions_path: str = os.getenv('REQUEST_CONDITIONS_PATH')
        self.request_conditions = bst.load_json_as_dic(request_conditions_path)
        self.current_index = 0
        
        pass

    def add_song_to_list(self, key:str, requester : twitchio.Chatter) -> None:

        file_path = self.playlist_path

        current_song_list = bst.get_songs_from_bplist(file_path)

        if len(current_song_list) >= int(self.queue_limit):
            return False, 'Playlist is full.'
        else:   
            count = 0
            for i,s in enumerate(current_song_list):
                if s.get('requester','')==requester.display_name:
                    count += 1
                if s.get('key') == key:
                    if i>self.current_index:
                        return False, 'This track is already in the queue'
                    else:
                        return False, 'This track has already been played'
        # check for already submitted song by this user
        if (not requester.moderator and 
            not requester.subscriber and 
            not requester.broadcaster):
            if count >= self.max_request_per_viewer:
                return False, f'max request per viewer is {self.max_request_per_viewer}'
        
        info = bst.get_song_info_by_id(key)
        if info is None:
            return False, f'this key do not exist: {key}'

        passed_check,log = bst.check_song_conditions(info,conditions=self.request_conditions)
        if passed_check:
            try:
                bst.add_song_to_bplist(file_path,info, 
                                       requester=requester.display_name
                                       )
            except Exception as e:
                log += f"\n Failed to add {key}. Reason: {e}"
                passed_check = False

        if passed_check:
            try:
                self.actualize_obs_queue()
            except Exception as e:
                log += f"\n Failed to update the overlay. Reason: {e}"
            log += f"\n Added {key} to the playlist."
        else:
            log += f"\n Failed to add {key} to the playlist"

        return passed_check,log
    

    def change_index(self,offset):
        self.current_index = max(self.current_index+offset,0)
        self.actualize_obs_queue()
        pass


    def reinitialize_playlist(self) -> None:
        bst.clear_songs_from_bplist(self.playlist_path)
        self.current_index = 0
        self.actualize_obs_queue()
        pass


    def actualize_obs_queue(self) -> None:
        current_song_list = bst.get_songs_from_bplist(self.playlist_path)

        if len(current_song_list) >0:
            current_text = f"Current: {current_song_list[self.current_index]['songName']}\n"            
        else:
            current_text = "No songs in playlist."


        if self.current_index > 0:
            previous_text = f"Previous: {current_song_list[self.current_index - 1]['songName']}\n"
        else:
            previous_text = "No song. played for now"

        if self.current_index < len(current_song_list) -1:
            next_text = f"Next: {current_song_list[self.current_index + 1]['songName']}\n"
        else:
            next_text = "This is the last song in the cue."

        bst.write_obs_txt(self.obs_txt_path+"current.txt", current_text)  
        bst.write_obs_txt(self.obs_txt_path+"previous.txt", previous_text)
        bst.write_obs_txt(self.obs_txt_path+"next.txt", next_text)


playlist = BeatSaberPlaylist()

if __name__ == "__main__":
    playlist.reinitialize_playlist()
    playlist.add_song_to_list('12345')
    
