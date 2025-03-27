# coding: UTF-8
# DiscordBot.py
import os
from keep import keep_alive
import traceback
import discord
import re
from discord.ext import commands
#from discord_slash import SlashCommand, SlashContext    #スラッシュcommandラブラリ

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


# #ロール付与
# ID_CHANNEL_README = 870211789340700703  # 該当のチャンネルのID
# ID_ROLE_WELCOME = 885772629083029515  # 付けたい役職のID

# @client.event
# async def on_raw_reaction_add(payload):
#     # channel_id から Channel オブジェクトを取得
#     channel = client.get_channel(payload.channel_id)

#     # 該当のチャンネル以外はスルー
#     if channel.id != ID_CHANNEL_README:
#         return

#     # guild_id から Guild オブジェクトを取得
#     guild = client.get_guild(payload.guild_id)

#     member = payload.member
#     #botならつけない
#     if member.bot:
#         return
#     # 用意した役職IDから Role オブジェクトを取得
#     role = guild.get_role(ID_ROLE_WELCOME)

#     # リアクションを付けたメンバーに役職を付与
#     await member.add_roles(role)
#     print("追加")

# @client.event
# async def on_raw_reaction_remove(payload):
#     # channel_id から Channel オブジェクトを取得
#     channel = client.get_channel(payload.channel_id)

#     # 該当のチャンネル以外はスルー
#     if channel.id != ID_CHANNEL_README:
#         return

#     # guild_id から Guild オブジェクトを取得
#     guild = client.get_guild(payload.guild_id)

#     # user_id から Member オブジェクトを取得
#     member = guild.get_member(payload.user_id)
#     if member.bot:
#         return
#     # 用意した役職IDから Role オブジェクトを取得
#     role = member.guild.get_role(885772629083029515)

#     # リアクションを付けたメンバーに役職を付与

#     await member.remove_roles(role)
#     print("削除")

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

    # if message.content == "/tlls":
    #     await message.channel.send("日本語:ja\n英語:en\n韓国語:ko\nドイツ語:de")
    #  #エラー　モジュール名なし
    # from googletrans import Translator #インポート
    # if message.content[:4] == "/tl:":#/tl:ja/en こんにちは
    #     translator = Translator()
    #     result = translator.translate(message.content[10:], src=f'{message.content[4:6]}', dest=f'{message.content[7:9]}')#メッセージ内容、翻訳前言語コード、翻訳語言語コード
    #     await message.channel.send( result.text)#メッセージの送信
    #     #await message.channel.send(translator.translate(f'{message.content[10:]}', src=f'{message.content[4:6]}' ,dest=f'{message.content[7:9]}').text)

    #     #await message.channel.send(f'https://translate.google.co.jp/?hl=ja&sl={message.content[4:6]}&tl={message.content[7:9]}&text={message.content[10:]}&op=translate')
    #     #apexトラッカー
    # from googletrans import Translator
    # if message.content[:3] == "/ko":
    #     translator = Translator()
    #     result = translator.translate(message.content[3:], src='ja', dest='ko')
    #     await message.channel.send( result.text)

    # if message.content[:3] == "/ja":
    #     from googletrans import Translator
    #     translator = Translator()
    #     result = translator.translate(message.content[3:], src='ko', dest='ja')
    #     await message.channel.send( result.text)

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

    # inappropriate_words = [
    #     "ばか","バカ","アホ","あほ","カス","かす","くず","クズ","死ね","しね","消えろ","きえろ","黙れ","だまれ","ゴミ","ごみ","クソ","くそ","変態","へんたい",
    #     "気持ち悪い","キモい","キモイ","きもい","キモ","気持ちわる","うざい","ウザい","ウザ","馬鹿","バカヤロウ","バカやろう","バカ野郎","ガキ","がき","幼稚",
    #     "ようち","ボケ","ボンクラ","低脳","ていのう","知恵遅れ","ちえおくれ","頭悪い","あたまわるい","脳なし","のうなし","デブ","でぶ","ブス","ぶす","不細工",
    #     "ぶさいく","不潔","ふけつ","臭い","くさい","ダサい","ださい","貧乏","びんぼう","金なし","かねなし","クチャラー","ガイジ","がいじ","池沼","いけぬま",
    #     "障害者","しょうがいしゃ","ヤクザ","やくざ","暴力団","キチガイ","キチ","狂ってる","イカれてる","おかしい","基地外","変人","へんじん","異常",
    #     "悪魔","最低","下品","クズ人間","人間のクズ","社会不適合者","カマ野郎","ホモ","オカマ","レズ","おかま","精神病","統失","パワハラ","セクハラ","いじめ",
    #     "イジメ","妄想","バーカ","ぶっ殺す","刺すぞ","殴るぞ","蹴るぞ","殺すぞ","ころすぞ","なぐる","しばく","ぶん殴る","お前","てめえ","貴様","うるせえ",
    #     "くたばれ","こいつ","あいつ","やつ","ド低能","阿呆","ドアホ","ガイキチ","ムカつく","ムカついた","ぶっ壊す","殺意","地獄へ落ちろ","落ちろ","吐き気",
    #     "ぶさいく","ちび","でかすぎ","顔でか","顔でかい","顔きも","腹黒","性格悪い","自己中","自意識過剰","ナルシスト","お前なんか","お前が悪い",
    #     "お前のせい","勝手にしろ","どっかいけ","親の顔が見たい","恥を知れ","消えてくれ","無理","話す価値なし","生きてる価値なし","いらない","迷惑",
    #     "生ゴミ","しつこい","めんどくさい","頭おかしい","変なやつ","嫌い","大嫌い","呪う","不幸になれ","呪われろ","見たくない","おえっ","センスない",
    #     "くるってる","見苦しい","見損なった","終わってる","絶望的","話にならない","異常者","気が狂ってる","人でなし","心がない","バグってる","負け犬",
    #     "役立たず","ゴキブリ","虫けら","腐ってる","カビ","しねしね","さよなら","お断り","論外","地雷","ブロックする","BAN","病気","メンヘラ","デンパ",
    #     "厨二病","イキリ","雑魚","ノータリン","能無し","何様","使えない","役に立たない","がっかり","絶対許さない","罰が当たる","汚い","吐く","気色悪い",
    #     "スベってる","痛い","ヤバいやつ","変な人","陰湿","陰険","ねちっこい"
    # ]

    # # 不適切な単語が含まれていれば注意メッセージを送信
    # for word in inappropriate_words:
    #     if re.search(re.escape(word), message.content, re.IGNORECASE):
    #         await message.channel.send(
    #             f'{message.author.name}さん、不適切な発言は控えましょう。')
    #         break


from discord.ext import tasks

# # 定期実行タスク：1時間ごとに実行
# @tasks.loop(hours=1)
# async def periodic_commands():
#     channel = client.get_channel(1292534892294438953)  # 送信先チャンネルのIDに置き換え
#     if channel is not None:
#         await channel.send("/bump")
#         await channel.send("/dissoku up")
#         print("定期コマンドを送信しました。")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    periodic_commands.start()

    # #特定のメッセージを消去、ユーザー名、ID表示
    # textChannelId = 866370772205174794
    # if message.channel.id == textChannelId:
    #     #if "http" in message.content:
    #     if re.search("http", message.content) and re.search(
    #             "://", message.content):  #もし先頭がhttpかつ、://を含む文字があれば
    #         await message.delete()
    #         if message.author.bot:  # メッセージ送信者がBotだった場合は無視する
    #             return
    #         else:

    #             await message.channel.send(
    #                 f'このチャンネルはURL貼り付け禁止です。messageを削除しました。\
    #              \nユーザー名:{message.author.name}ユーザーID:{message.author.id}')

    # if message.content == "/Hellobot":
    #     await message.channel.send("""---------Hellobotの機能-----------\n
    #     入退出ログ\n
    #     VC参加者ロール\n
    #     Discordlive配信者ロール\n
    #     リアクションロール（カスタム関連のみ）\n
    #     URL貼り付け禁止(自己紹介のみ)\n
    #     /neko\n
    #     /HelloTwitter\n
    #     /tlls
    #     /tl:翻訳前言語コード/翻訳後言語コード テキスト\n
    #     /ko 韓国語に翻訳\n
    #     /ja 일본어로 번역\n
    #     /apex:originプレイヤーID\n
    #     """)


# Botのトークンを指定（デベロッパーサイトで確認可能）
server_thread()
client.run(TOKEN))
