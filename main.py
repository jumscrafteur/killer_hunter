from schedule import every, repeat, run_pending
import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = 'https://discord.com/api/webhooks/1042192841784442900/QfeFI0HzR6mxZf7IoLEwfiIl5ptR3STPFP0g6N4qnXoJFtL90wUvykxbwRQN1JDe2ggi'
INSTA_URL = 'https://www.instagram.com/api/v1/feed/user/insa_cvl_crush/username/?count=3'

INSTA_HEADERS = {
    'x-ig-app-id': os.environ.get('INSTAGRAM_APP_ID')
}

DISCORD_MSG_TEMPLATE = {
    "username": "Killer Hunter | INSA Crush",
    "embeds": [
        {
                "title": "Nouveaux Post sur @insa_cvl_crush",
                "image": {
                    "name": "post",
                    "url": "https://via.placeholder.com/845"
                }
        }
    ]
}

now = datetime.datetime.now()

nowStr = f"[{now.hour:02d}:{now.minute:02d}:{now.second:02d}]"

try:
    r = requests.get(INSTA_URL, headers=INSTA_HEADERS)
    instagramData = r.json()

    lastPostId = instagramData['items'][0]["id"]
except requests.exceptions.HTTPError as err:
    print(f'{nowStr} 🟥 | {err}')


@repeat(every(1).to(2).hours)
def job():
    global lastPostId

    now = datetime.datetime.now()

    nowStr = f"[{now.hour:02d}:{now.minute:02d}:{now.second:02d}]"

    print(f'{nowStr} ⏳ | Récupération des 3 derniers post Insta de @insa_cvl_crush')

    r = requests.get(INSTA_URL, headers=INSTA_HEADERS)
    discordAPIData = r.json()

    newPosts = []

    for i in range(3):
        post = discordAPIData['items'][i]
        if post['id'] == lastPostId:
            break
        print(f'{nowStr} 🥳 | Nouveaux Post: { post["id"] }')
        newPosts.append(
            (post['id'], post['image_versions2']['candidates'][0]['url']))

    lastPostId = newPosts[0][0] if len(newPosts) > 0 else lastPostId

    newPosts = newPosts[::-1]

    for post in newPosts:
        discordMsgData = DISCORD_MSG_TEMPLATE
        discordMsgData["embeds"][0]["image"]["url"] = post[1]

        result = requests.post(WEBHOOK_URL, json=discordMsgData)
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f'{nowStr} 🟥 | {err}')
        else:
            print(
                f'{nowStr} ✅ | Message envoyé (code {result.status_code})')


job()


while True:
    run_pending()
