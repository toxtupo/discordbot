# coding: UTF-8
import os
import traceback
import discord
import re
from discord.ext import commands, tasks  # tasksは定期実行用
from server import server_thread
import dotenv

# .envから環境変数（TOKEN）を読み込む
dotenv.load_dotenv()
TOKEN = os.environ.get("TOKEN")

# === Botの設定 ===
# DiscordのIntentsを設定（必要なイベントを受け取るため）
intents = discord.Intents.default()
intents.members = True            # メンバーの参加/退出等のイベントを取得
intents.message_content = True    # メッセージ内容を取得（コマンド処理用）
intents.guilds = True             # サーバー情報を取得
intents.reactions = True          # リアクションのイベントを取得

client = discord.Client(intents=intents)

# === 各種ID・変数の定義（すべてここに集約） ===
# チャンネルID
WELCOME_CHANNEL_ID = 1292515991812702279   # ウェルカムメッセージ送信先チャンネルのID
SELF_INTRO_CHANNEL_ID = 1292752418223951892  # 自己紹介用チャンネルのID
RULES_CHANNEL_ID = 1292752495155875860         # ルールチャンネルのID
TARGET_CHANNEL_ID = 1354692158187114598        # リアクションロール用メッセージが投稿されているチャンネルのID
TARGET_MESSAGE_ID = 1354713468259008657        # リアクションロール用メッセージのID

# ロールID
ACCESS_ROLE_ID = 1347884514940031027  # 自己紹介完了後に付与される閲覧可能ロールのID

# リアクションとロールの対応（絵文字: ロールID）
REACTION_ROLE_MAP = {
    "🇦": 1354684922455130113,  # 絵文字🇦 に対応するロール（例: ロールA）
    "🇧": 1354693071073185984,  # 絵文字🇧 に対応するロール（例: ロールB）
    "🇨": 1354693249843069038,  # 絵文字🇨 に対応するロール（例: ロールC）
    "🇩": 1354694164578828468,  # 絵文字🇩 に対応するロール（例: ロールD）
    "🇪": 1354694445630492762,  # 絵文字🇪 に対応するロール（例: ロールE）
    "🇫": 1354694498210283613,  # 絵文字🇫 に対応するロール（例: ロールF）
    "🇬": 100000000000000007,   # 絵文字🇬 に対応するロール（例: ロールG）
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
