# Internal modules
import asyncio
import time
import logging
from typing import Optional

# Project modules
from nlp import is_time_request_spacy, sanitize_text
from constants import *

# External modules
import discord
from discord import SlashCommand, TextChannel


class MerciArtemisPourLheure(discord.Client):
    """
    This class is the main MerciArtemisPourLheure bot class
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the bot and the worker thread
        """
        super().__init__(**kwargs)

        # Discord resources
        self.artemis_channel: Optional[TextChannel] = None
        self.artemis_command: Optional[SlashCommand] = None
        self.message_requests: list[discord.Message] = []

        # Pause system
        self.disabled_until: int = 0

        # Throttling system
        self.last_message_time = 0

        # Logging system
        logging.basicConfig(
            level=logging.INFO, format="\x1b[0m%(asctime)s %(levelname)s %(message)s"
        )

    async def on_ready(self) -> None:
        """
        Internally called method when the bot is ready, here it starts the worker thread
        :return: None
        """
        logging.info(f"Authenticated as {self.user} (ID: {self.user.id})\n")

        # Get artemis channel
        try:
            self.artemis_channel = await self.fetch_channel(ARTEMIS_CHANNEL_ID)
        except (
            discord.InvalidData,
            discord.HTTPException,
            discord.NotFound,
            discord.Forbidden,
        ):
            logging.critical(
                f"Channel {ARTEMIS_CHANNEL_ID} can't be accessed, please check your configuration."
            )
            await self.close()
            return

        # Get heure command
        for command in await self.artemis_channel.application_commands():
            if command.name == "heure":
                logging.info(f"Found command {command.name} (id: {command.id})")
                self.artemis_command = command
        if not self.artemis_command:
            logging.critical("Command /heure not found, please check your configuration.")
            await self.close()
            return
        logging.info("Bot is ready!")

    async def on_message(self, message: discord.Message) -> None:
        """
        This method is internally called when a message is received
        :param message: The message received
        :return: None
        """
        # If the bot is temporarily disabled, ignore
        if self.disabled_until > time.time():
            return

        # If not in targeted guild, ignore
        if message.guild.id != GUILD_ID:
            return

        # Transmis latest Artemis dit l'heure message to top request in the list
        if message.author.id == ARTEMIS_ID:
            await self.on_artemis(message)
            return

        # If the message is not from Artemis or a bot, determine if it's a time request
        if message.author.bot:
            return

        await self.on_new_message(message)

    async def on_artemis(self, message: discord.Message) -> None:
        """
        This method is internally called when a message is received from the Artemis bot
        :param message: The message received
        :return: None
        """
        # Get the top request in the list
        if self.message_requests:
            request = self.message_requests.pop(0)
            await self.delayed_send(message.reply, f"Merci pour tes loyaux services Artémis ! Je transmet l'information à {request.author.mention}")
            await self.delayed_send(request.reply, f"D'après {message.author.mention}, {message.content.lower()}")

    async def on_new_message(self, message: discord.Message) -> None:
        """
        This method is called when a new message is received to determine if it's a time request
        :param message: The message received
        :return: None
        """
        if message.guild.me in message.mentions and "ta gueule" in sanitize_text(message.content):
            logging.info(f"Shut up request detected from {message.author}: {message.content}")
            logging.info(f"Bot disabled until {time.time() + 900}")
            self.disabled_until = time.time() + 900
            await self.delayed_send(message.reply, "Padooon <:blobono:1187429702445576242>\nJe me tais 15 minutes.")
            return
        if not is_time_request_spacy(message.content):
            return
        logging.info(f"Time request detected from {message.author}: {message.content}")
        self.message_requests.append(message)
        await self.artemis_command.__call__(channel=self.artemis_channel, format="Lettres")

    async def delayed_send(self, function, *args, **kwargs):
        """
        Send a message with a minimum 1-second delay since last message
        :param function: The function to call
        :param args: The function arguments
        :param kwargs: The function keyword arguments
        :return: The result of the function
        """
        # Calculate time since last message and wait the remaining time if applicable
        elapsed = time.time() - self.last_message_time
        if elapsed < DELAY_BETWEEN_MESSAGES:
            await asyncio.sleep(DELAY_BETWEEN_MESSAGES - elapsed)

        # Send the message and update timestamp
        result = await function(*args, **kwargs)
        self.last_message_time = time.time()
        return result

if __name__ == "__main__":
    client = MerciArtemisPourLheure(status=discord.Status.invisible)
    client.run(TOKEN)
