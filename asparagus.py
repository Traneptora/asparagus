#!/usr/bin/env python3

import asyncio, signal
import os, re, sys, time
import traceback

import discord
import requests
from discord.ext import tasks

from deepbluesky import DeepBlueSky

# constants / globals

TBWF_GUILD_ID = 296109704579383297
TBWF_ANNOUNCE_CHANNEL_ID = 416584397668483082
TBWF_COMIC_UPDATE_PING_ROLE_ID = 453193242989821953
TBWF_EXTRA_UPDATE_PING_ROLE_ID = 878077675762221066

client = DeepBlueSky(bot_name='asparagus')

# rss stuffs

@tasks.loop(minutes = 30)
async def retrieve_rss():
    os.makedirs('feed/', mode=0o755, exist_ok=True)
    await retrieve_latest('feed/the_boy_who_fell', 'https://boywhofell.com/comic/rss', re.compile(r'<link>(https://www\.boywhofell\.com/comic/.*?)</link>'), '**New Page:** The Boy Who Fell!', TBWF_COMIC_UPDATE_PING_ROLE_ID)
    await asyncio.sleep(15)
    await retrieve_latest('feed/springtime_of_yuuth', 'https://tapas.io/rss/series/91928', re.compile(r'<link>(https://tapas\.io/episode/[0-9]+)</link>'), '**New Page:** Springtime of Yuuth!', TBWF_EXTRA_UPDATE_PING_ROLE_ID)  
    await asyncio.sleep(15)
    await retrieve_latest('feed/falltime_of_ren', 'https://tapas.io/rss/series/187508', re.compile(r'<link>(https://tapas\.io/episode/[0-9]+)</link>'), '**New Page:** Falltime of Ren!', TBWF_EXTRA_UPDATE_PING_ROLE_ID)
    await asyncio.sleep(15)
    await retrieve_latest('feed/yuu_vs_the_cosmic_unknown', 'https://tapas.io/rss/series/215720', re.compile(r'<link>(https://tapas\.io/episode/[0-9]+)</link>'), '**New Page:** Yuu vs the Cosmic Unknown!', TBWF_EXTRA_UPDATE_PING_ROLE_ID)
    await asyncio.sleep(15)
    await retrieve_latest('feed/mapmaker', 'https://tapas.io/rss/series/238857', re.compile(r'<link>(https://tapas\.io/episode/[0-9]+)</link>'), '**New Page:** Mapmaker!', TBWF_EXTRA_UPDATE_PING_ROLE_ID)

async def retrieve_latest(cache_filename, url, regex, new_page_prefix, ping_role):
    remote_version = None
    try:
        response = requests.get(url, headers={'User-Agent': 'curl/7.76.1'}, timeout=5)
        for line in response.text.split('\n'):
            match = regex.search(line)
            if match:
                remote_version = match.group(1)
                break
    except Exception as error:
        client.logger.exception('Unable to obtain remote version')
    if remote_version is None:
        client.logger.error(f'Error retreieving latest remote: {url}')
        return

    try:
        with open(cache_filename, 'r', encoding='UTF-8') as cache_file:
            cached_version = cache_file.read()
    except IOError:
        cached_version = ''

    if remote_version != cached_version:
        client.logger.info(f'Found update: {cache_filename}')
        channel_id = TBWF_ANNOUNCE_CHANNEL_ID
        channel = client.get_channel(channel_id)
        if channel:
            await client.send_to_channel(channel, None, f'<@&{ping_role}> {new_page_prefix} {remote_version}', ping_roles=[ping_role])
        else:
            client.logger.error(f'Invalid channel: {channel_id}')
        with open(cache_filename, 'w', encoding='UTF-8') as cache_file:
            cache_file.write(remote_version)
    else:
        client.logger.info(f'Already up to date: {cache_filename}')

# discord events

@client.event
async def on_ready():
    client.logger.info(f'Logged in as {client.user}')
    game = discord.Game('I’m an Asparagus')
    await client.change_presence(status=discord.Status.online, activity=game)
    retrieve_rss.start()

client.run()
