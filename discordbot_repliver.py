# coding: UTF-8
# DiscordBot.py
import os
#from keep import keep_alive
import traceback
import discord
import re
from discord.ext import commands


#from discord_slash import SlashCommand, SlashContext    #スラッシュcommandラブラリ

#Koyebで追加
from server import server_thread
import dotenv
dotenv.load_dotenv()
TOKEN = os.environ.get("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # 念のため
intents.guilds = True
intents.reactions = True  # ←重要

#bot = discord.Client(intents_discord.Intents.all())
#slash_client = SlashCommand(bot, sync_commands=True)

client = discord.Client(intents=intents)
''' チャンネル指定　自由部屋と映画館
# チャンネル入退室時の通知処理
@client.event
async def on_voice_state_update(member, before, after):

    # チャンネルへの入室ステータスが変更されたとき（ミュートON、OFFに反応しないように分岐）
    if before.channel != after.channel:
        # 通知メッセージを書き込むテキストチャンネル（チャンネルIDを指定）
        botRoom = client.get_channel(871422782171402351)

        # 入退室を監視する対象のボイスチャンネル（チャンネルIDを指定） 自由部屋と映画館
        announceChannelIds = [871089074855882853, 866746830082277406]

        # 退室通知
        if before.channel is not None and before.channel.id in announceChannelIds:
            await botRoom.send("**" + before.channel.name + "** から、__" + member.name + "__  が抜けました！")
        # 入室通知
        if after.channel is not None and after.channel.id in announceChannelIds:
            await botRoom.send("**" + after.channel.name + "** に、__" + member.name + "__  が参加しました！")

'''


#サーバー全体No documentation available
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# #Voiceevent
# @client.event
# async def on_voice_state_update(member, before, after):
#     #入退出andVC参加ロール
#     if member.guild.id == 866368955597979658:
#         text_ch = client.get_channel(871422782171402351)
#         if before.channel is None:
#             #  msg = f'{member.name} が {after.channel.name} に参加しました。'
#             await text_ch.send("**" + after.channel.name + "** に、__" +
#                                member.name + "__  が参加しました！")
#             #通話参加中ロール
#             role = member.guild.get_role(876862473427378226)
#             await member.add_roles(role)

#         if after.channel is None:
#             #  msg = f'{member.name} が {before.channel.name} に退出'
#             await text_ch.send("**" + before.channel.name + "** から、__" +
#                                member.name + "__  が抜けました！")
#             #通話参加中ロール
#             role = member.guild.get_role(876862473427378226)
#             await member.remove_roles(role)

#             #もしliveを終了せずvcを抜けた時のroll処理
#             role = member.guild.get_role(876857452925173772)
#             await member.remove_roles(role)

#         #discordのlive配信を始めたらロール付与やめたらロールはく奪
#         if before.channel and after.channel:  # If a user is connected before and after the update
#             if before.self_stream != after.self_stream:
#                 role = member.guild.get_role(876857452925173772)
#                 await member.add_roles(role)

#             if before.self_stream != False:
#                 role = member.guild.get_role(876857452925173772)
#                 await member.remove_roles(role)

#ロール付与改良版
# ==== 設定値をここに書く ====
TARGET_CHANNEL_ID = 1354692158187114598  # 手動投稿したメッセージのあるチャンネルのID
TARGET_MESSAGE_ID = 1354713468259008657  # 手動投稿したメッセージのID

# リアクションとロールの対応（絵文字: ロールID）
REACTION_ROLE_MAP = {
    "🇦": 1354684922455130113,  # A
    "🇧": 1354693071073185984,  # B
    "🇨": 1354693249843069038,  # C
    "🇩": 1354694164578828468,  # D
    "🇪": 1354694445630492762,  # E
    "🇫": 1354694498210283613,  # F
    "🇬": 100000000000000007,  # G
    "🇭": 100000000000000008,  # H
    "🇮": 100000000000000009,  # I
    "🇯": 100000000000000010,  # J
    "🇰": 100000000000000011,  # K
    "🇱": 100000000000000012,  # L
    "🇲": 100000000000000013,  # M
    "🇳": 100000000000000014,  # N
    "🇴": 100000000000000015,  # O
    "🇵": 100000000000000016,  # P
    "🇶": 100000000000000017,  # Q
    "🇷": 100000000000000018,  # R
    "🇸": 1354694596432756841,  # S
    "🇹": 1354694635405967380,  # T
}


# ==== リアクションが追加されたとき ====
@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id != TARGET_CHANNEL_ID or payload.message_id != TARGET_MESSAGE_ID:
        return

    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return

    emoji = payload.emoji.name  # 例: "1️⃣"
    role_id = REACTION_ROLE_MAP.get(emoji)
    if role_id is None:
        return

    role = guild.get_role(role_id)
    member = guild.get_member(payload.user_id)

    if role and member and not member.bot:
        await member.add_roles(role)
        print(f"{member.name} にロール {role.name} を付与しました")


# ==== リアクションが削除されたとき ====
@client.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id != TARGET_CHANNEL_ID or payload.message_id != TARGET_MESSAGE_ID:
        return

    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return

    emoji = payload.emoji.name
    role_id = REACTION_ROLE_MAP.get(emoji)
    if role_id is None:
        return

    role = guild.get_role(role_id)
    member = guild.get_member(payload.user_id)

    if role and member and not member.bot:
        await member.remove_roles(role)
        print(f"{member.name} からロール {role.name} を削除しました")


SELF_INTRO_CHANNEL_ID = 1292752418223951892  # 自己紹介用チャンネルのID
ACCESS_ROLE_ID = 1347884514940031027  # 閲覧可能なロールのID


@client.event
async def on_message(message):
    # Bot のメッセージは無視
    if message.author.bot:
        return

    # ① 自己紹介用の処理
    if message.channel.id == SELF_INTRO_CHANNEL_ID:
        if "【名前】" in message.content:
            role = message.guild.get_role(ACCESS_ROLE_ID)
            if role is None:
                print("指定されたロールが見つかりません。")
            elif role not in message.author.roles:
                try:
                    await message.author.add_roles(role)
                    print(f"{message.author.name} にロール {role.name} を付与しました。")
                    await message.channel.send(
                        f"{message.author.mention} さん、自己紹介ありがとうございます！")
                except Exception as e:
                    print(f"ロール付与エラー: {e}")
            else:
                print(f"{message.author.name} は既にロール {role.name} を持っています。")

    # ② コマンド処理（例：/neko）
    if message.content == "/neko":
        await message.channel.send("にゃーん!")



    if message.content[:6] == "/valo:":
        await message.channel.send(
            f'https://tracker.gg/valorant/profile/riot/{meｓsage.content[6:len(meｓsage.content)]}/overview'
        )
    if message.content[:6] == "/apex:":
        await message.channel.send(
            f'https://apex.tracker.gg/apex/profile/origin/{meｓsage.content[6:len(meｓsage.content)]}/overview'
        )

    if message.author.bot:
        return

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    periodic_commands.start()


# Botのトークンを指定（デベロッパーサイトで確認可能）
server_thread()
client.run(TOKEN)
