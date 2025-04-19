# coding: UTF-8
import os
import traceback
import discord
import re
from discord.ext import commands, tasks  # tasksは定期実行用
from server import server_thread
import dotenv
import requests
from bs4 import BeautifulSoup
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# .envから環境変数（TOKEN）を読み込む
dotenv.load_dotenv()
TOKEN = os.environ.get("TOKEN")
creds_json = os.environ["GOOGLE_CREDS_JSON"]
creds_dict = json.loads(creds_json)

# === Botの設定 ===
# DiscordのIntentsを設定（必要なイベントを受け取るため）
intents = discord.Intents.default()
intents.members = True            # メンバーの参加/退出等のイベントを取得
intents.message_content = True    # メッセージ内容を取得（コマンド処理用）
intents.guilds = True             # サーバー情報を取得
intents.reactions = True          # リアクションのイベントを取得
intents.presences = True

client = discord.Client(intents=intents)

# === 各種ID・変数の定義（すべてここに集約） ===
# チャンネルID
WELCOME_CHANNEL_ID = 1292515991812702279   # ウェルカムメッセージ送信先チャンネルのID
SELF_INTRO_CHANNEL_ID = 1292752418223951892  # 自己紹介用チャンネルのID
RULES_CHANNEL_ID = 1292752495155875860         # ルールチャンネルのID
TARGET_CHANNEL_ID = 1354692158187114598        # リアクションロール用メッセージが投稿されているチャンネルのID
TARGET_MESSAGE_ID = 1354713468259008657        # リアクションロール用メッセージのID
CUSTOM_RECRUIT_CHANNEL_ID = 1352877089501483059  # カスタム募集用チャンネルのID（このチャンネル内でのみ募集スレッド作成機能を実行）
CUSTOM_RECRUIT_ROLE_ID = 1355494037490237490  # カスタム募集ロールのID
PROFILE_CHANNEL_ID = 1354674412418502858    #profile登録チャンネルID
PROFILE_FILE = "/tmp/profiles.json"
ACCESS_ROLE_ID = 1347884514940031027  # 自己紹介完了後に付与される閲覧可能ロールのID
# 登録中ユーザーの一時管理
user_profile_sessions = {}  # {user_id: {"nickname": str, "thread": discord.Thread, "lines": []}}

# リアクションとロールの対応（絵文字: ロールID）
REACTION_ROLE_MAP = {
    "🇦": 1354684922455130113,  # 絵文字🇦 に対応するロール（例: ロールA）
    "🇧": 1354693071073185984,  # 絵文字🇧 に対応するロール（例: ロールB）
    "🇨": 1354693249843069038,  # 絵文字🇨 に対応するロール（例: ロールC）
    "🇩": 1354694164578828468,  # 絵文字🇩 に対応するロール（例: ロールD）
    "🇪": 1354694445630492762,  # 絵文字🇪 に対応するロール（例: ロールE）
    "🇫": 1354694498210283613,  # 絵文字🇫 に対応するロール（例: ロールF）
    "🇬": 1362957716221329469,   # 絵文字🇬 に対応するロール（例: ロールG）
    "🇭": 100000000000000008,   # 絵文字🇭 に対応するロール（例: ロールH）
    "🇮": 100000000000000009,   # 絵文字🇮 に対応するロール（例: ロールI）
    "🇯": 100000000000000010,   # 絵文字🇯 に対応するロール（例: ロールJ）
    "🇰": 100000000000000011,   # 絵文字🇰 に対応するロール（例: ロールK）
    "🇱": 100000000000000012,   # 絵文字🇱 に対応するロール（例: ロールL）
    "🇲": 100000000000000013,   # 絵文字🇲 に対応するロール（例: ロールM）
    "🇳": 100000000000000014,   # 絵文字🇳 に対応するロール（例: ロールN）
    "🇴": 100000000000000015,   # 絵文字🇴 に対応するロール（例: ロールO）
    "🇵": 100000000000000016,   # 絵文字🇵 に対応するロール（例: ロールP）
    "🇶": 100000000000000017,   # 絵文字🇶 に対応するロール（例: ロールQ）
    "🇷": 1355320836562620477,   # 絵文字🇷 に対応するロール（例: ロールR）
    "🇸": 1354694596432756841,  # 絵文字🇸 に対応するロール（例: ロールS）
    "🇹": 1354694635405967380,  # 絵文字🇹 に対応するロール（例: ロールT）
}

# === 定期実行タスク（必要なら使用） ===


# === イベントハンドラー群 ===

# on_ready: Botの起動時に呼ばれる
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

# リアクションが追加されたときの処理
@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id != TARGET_CHANNEL_ID or payload.message_id != TARGET_MESSAGE_ID:
        return

    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return

    emoji = payload.emoji.name  # 例: "🇦"
    role_id = REACTION_ROLE_MAP.get(emoji)
    if role_id is None:
        return

    role = guild.get_role(role_id)
    member = guild.get_member(payload.user_id)
    if role and member and not member.bot:
        await member.add_roles(role)
        print(f"{member.name} にロール {role.name} を付与しました")

# リアクションが削除されたときの処理
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

# on_message: メッセージイベントの処理
# MESSAGE_THREAD_MAP = {} #カスタム募集スレッド作成用
@client.event
async def on_message(message):
    # Botのメッセージは無視
    if message.author.bot:
        return
        
    # 自己紹介用チャンネルで自己紹介（「【名前】」が含まれる場合）の処理
    if message.channel.id == SELF_INTRO_CHANNEL_ID:
        if "【名前】" in message.content:
            role = message.guild.get_role(ACCESS_ROLE_ID)
            if role is None:
                print("指定されたロールが見つかりません。")
            elif role not in message.author.roles:
                try:
                    await message.author.add_roles(role)
                    print(f"{message.author.name} にロール {role.name} を付与しました。")
                    await message.channel.send(f"{message.author.mention} さん、自己紹介ありがとうございます！")
                except Exception as e:
                    print(f"ロール付与エラー: {e}")
            else:
                print(f"{message.author.name} は既にロール {role.name} を持っています。")

    # ----- 自動スレッド作成機能（カスタム募集チャンネルのみ） -----
    if (
        message.channel.id == CUSTOM_RECRUIT_CHANNEL_ID
        and any(role.id == CUSTOM_RECRUIT_ROLE_ID for role in message.role_mentions)
    ):
        try:
            thread_name = f"{message.author.display_name}さんの募集"
            thread = await message.create_thread(
                name=thread_name,
                auto_archive_duration=60  # 1時間で自動アーカイブ
            )
            await thread.send(f"{message.author.display_name}さんの募集についての質問や相談は本スレッドでお願いします！")
            print(f"スレッド '{thread_name}' を作成しました。")
        except Exception as e:
            print(f"スレッド作成エラー: {e}")



    # /games コマンド
    if message.content == "/gamesls":
        activity_counts = {}

        for member in message.guild.members:
            for activity in member.activities:
                if activity.type == discord.ActivityType.playing and activity.name:
                    game_name = activity.name
                    activity_counts[game_name] = activity_counts.get(game_name, 0) + 1

        if activity_counts:
            result = "🎮 サーバー内の現在のゲーム状況\n\n"
            for game, count in activity_counts.items():
                result += f"{game}：{count}人\n"
        else:
            result = "現在ゲームをプレイしているメンバーはいません。"

        await message.channel.send(result)


    
    
    # /neko コマンドの処理
    if message.content == "/neko":
        await message.channel.send("にゃーん!")

    # /valo: コマンドの処理（Valorantプロフィールのリンクを送信）
    if message.content[:6] == "/valo:":
        await message.channel.send(
            f'https://tracker.gg/valorant/profile/riot/{message.content[6:]}/overview'
        )

    # /apex: コマンドの処理（Apexプロフィールのリンクを送信）
    if message.content[:6] == "/apex:":
        await message.channel.send(
            f'https://apex.tracker.gg/apex/profile/origin/{message.content[6:]}/overview'
        )
#★★profile登録コマンド------------------------------------------------------------------------------------
 # スレッドでのプロフィール入力中処理
    if message.channel.type == discord.ChannelType.public_thread:
        for uid, sess in user_profile_sessions.items():
            if sess["thread"].id == message.channel.id and message.author.id == uid:
                if message.content.lower().strip() == "完了":
                    content = "\n".join(sess["lines"]).strip()
                    if not content:
                        await message.channel.send("なんにも書いてないみたい…！")
                        return

                    success, msg = save_profile(sess["nickname"], uid, content)
                    await message.channel.send(msg)
                    await message.channel.delete()
                    del user_profile_sessions[uid]
                else:
                    if len(sess["lines"]) >= 10:
                        await message.channel.send("ごめんね、10行までしかかけないの〜！")
                    else:
                        sess["lines"].append(message.content)
                return

    # プロフィール設定開始（コマンド受付：/setp ニックネーム）
    if message.channel.id == PROFILE_CHANNEL_ID and message.content.startswith("/setp "):
        nickname = message.content[6:].strip()
        if not nickname:
            await message.channel.send("ニックネーム、わすれてるよ〜！")
            return

        # 重複チェック
        if os.path.exists(PROFILE_FILE):
            try:
                with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                    profiles = json.load(f)
            except json.JSONDecodeError:
                profiles = {}  # 空ファイルなどによるデコード失敗対応
        else:
            profiles = {}

        if nickname in profiles and profiles[nickname]["user_id"] != message.author.id:
            await message.channel.send("そのニックネームはもう使われてるみたい…！")
            return


        try:
            thread = await message.channel.create_thread(
                name=f"{nickname} のぷろふぃーるとうろく✏️",
                type=discord.ChannelType.public_thread,
                auto_archive_duration=60
            )
            await thread.send(f"{message.author.mention} さん！ぷろふぃーるを10行までここに書いてねっ！\nぜんぶかけたら「完了」って送ってね〜！")
            user_profile_sessions[message.author.id] = {
                "nickname": nickname,
                "thread": thread,
                "lines": []
            }
        except Exception as e:
            print("スレッド作成エラー:", e)
            await message.channel.send("スレッドつくれなかったよ〜ごめんね…！")

    # プロフィール表示機能（例：/yuto）
    if message.content.startswith("/p"):
        command = message.content[3:].strip()
    
        try:
            # Google Sheets 接続
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client_gs = gspread.authorize(creds)
            sheet = client_gs.open("プロフィールリスト").sheet1
    
            values = sheet.get_all_values()  # 2次元リストで全データ取得
            headers = values[0]
            rows = values[1:]  # ヘッダーを除いたデータ
    
            for row in rows:
                data = dict(zip(headers, row))  # ヘッダーと行を辞書に
                if data["nickname"] == command:
                    content = data["content"]
                    await message.channel.send(f"📝 **{command}** のプロフィール\n```{content}```")
                    return
    
            await message.channel.send("そのプロフィール、見つからなかったよ〜！")
        except Exception as e:
            print("プロフィール表示エラー:", repr(e))
            await message.channel.send("よみこみに失敗しちゃった…ごめんね〜！")



# プロフィール保存用関数
def save_profile(nickname, user_id, content):
    try:
        # Google Sheets 認証設定
        # グローバルスコープで初期化済の `creds_dict` を使う
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        # シート名（またはスプレッドシートID）で開く
        sheet = client.open("プロフィールリスト").sheet1  # スプレッドシートのタイトルに合わせてください

        # 重複チェック（nickname が既にあるか確認）
        existing = sheet.col_values(1)  # 1列目に nickname を入れてる前提
        if nickname in existing:
            # 既に存在するnicknameは上書き不可（エラーメッセージ）
            row = existing.index(nickname) + 1
            row_user_id = sheet.cell(row, 2).value
            if str(user_id) != row_user_id:
                return False, "そのニックネームはもう使われてるみたい…！"

            # 上書きOKな場合（同一ユーザー）
            sheet.update_cell(row, 3, content)
            return True, "ぷろふぃーる、あっぷでーとできたよ〜！"

        # 新規追加
        sheet.append_row([nickname, str(user_id), content])
        return True, "とうろくできたよ〜！ありがとねっ"

    except Exception as e:
        print("Google Sheets 書き込みエラー:", e)
        return False, "なんかうまくいかなかったかも…！"




# on_member_join: サーバー参加時にウェルカムメッセージを送信し、自己紹介を促す
@client.event
async def on_member_join(member):
    # ウェルカムチャンネルの取得
    welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    # 自己紹介チャンネルの取得（メンション形式）
    self_intro_channel = member.guild.get_channel(SELF_INTRO_CHANNEL_ID)
    intro_link = self_intro_channel.mention if self_intro_channel else "自己紹介チャンネル"
    # ルールチャンネルの取得（メンション形式）
    rules_channel = member.guild.get_channel(RULES_CHANNEL_ID)
    rules_link = rules_channel.mention if rules_channel else "ルールチャンネル"
    
    if welcome_channel:
        welcome_message = (
            f"ようこそ {member.mention} さん！\n"
            f"サーバーに参加いただきありがとうございます！\n"
            f"まずは、以下のルールチャンネルをご確認ください：{rules_link}\n"
            f"をご理解いただいた上で、{intro_link} にて自己紹介をお願いします！\n"
            f"自己紹介後、他のチャンネルが閲覧できるようになります！"
        )
        try:
            await welcome_channel.send(welcome_message)
            print(f"ウェルカムメッセージを {member.name} さんに送信しました。")
        except Exception as e:
            print(f"ウェルカムメッセージ送信エラー: {e}")


# === Botの起動 ===
server_thread()  # サーバー関連の機能（例: keep_alive）を起動
client.run(TOKEN)
