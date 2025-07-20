import twitchio
from twitchio import eventsub
from twitchio.ext import commands
import random

import os
from .beatsaber import bs_tools as bst
from dotenv import load_dotenv

# C:\Users\d0t\Desktop\DEV\Twitch_bot\Components\beatsaber\bsr.env
load_dotenv(r'./Components/beatsaber/bsr.env')



class BeatsaberComponent(commands.Component):
    # An example of a Component with some simple commands and listeners
    # You can use Components within modules for a more organized codebase and hot-reloading.

    def __init__(self,) -> None: # bot: Bot
        # Passing args is not required...
        # We pass bot here as an example...
        # self.bot = bot
        pass

    # An example of listening to an event
    # We use a listener in our Component to display the messages received.
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")

    @commands.command()
    async def help(self, ctx: commands.Context) -> None:
        """Command that lists available commands for Beatsaber
        """
        await ctx.reply(f"Hi {ctx.chatter}!")

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
            passed_check,log = playlist.add_song_to_list(message)
        except Exception as e:
            passed_check = False
            log = f"  Error adding song: {e}"

        if passed_check:
            await ctx.send(log)
        else:
            await ctx.send(log)



    @commands.command()
    async def say(self, ctx: commands.Context, *, message: str) -> None:
        """Command which repeats what the invoker sends.

        !say <message>
        """
        await ctx.send(message)

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
        self.current_index = 0
        
        pass

    def add_song_to_list(self, key:str) -> None:
        current_song_list = bst.get_songs_from_bplist(self.playlist_path)

        if len(current_song_list) >= int(self.queue_limit):
            return False, 'Playlist is full.'

        file_path = self.playlist_path
        info = bst.get_song_info_by_id(key)
        passed_check,log = bst.check_song_conditions(info)
        if passed_check:
            try:
                bst.add_song_to_bplist(file_path,info)
            except Exception as e:
                log += f"\n{log} - Failed to add {key}. Reason: {e}"
                passed_check = False

        if passed_check:
            try:
                self.actualize_obs_queue()
            except Exception as e:
                log += f"\n{log} - Failed to update the overlay. Reason: {e}"
            log += f"\n{log} - Added {key} to the playlist."
        else:
            log += f"\n{log} - Failed to add {key} to the playlist"

        

        return passed_check,log



    def reinitialize_playlist(self) -> None:
        bst.clear_songs_from_bplist(self.playlist_path)
        self.current_index = 0
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
    
