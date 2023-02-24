from notionai import NotionAI # pip install --upgrade notionai-py
from tistory import Tistory # pip install tistory
import openai # pip install openai
import markdown # pip install markdown
from translate import Translator # pip install translate
import requests
import urllib.request
from config import *

TOPIC = '사람들을 웃기는 방법'

###################
# 0. Prepare APIs #
###################
notion_ai = NotionAI(NOTION_TOKEN, NOTION_SPACE_ID)
ts = Tistory(BLOG_URL, CLIENT_ID, CLIENT_SECRET)
ts.access_token = ACCESS_TOKEN
openai.api_key = OPENAI_API_KEY

translator = Translator(from_lang='ko', to_lang='en')

########################
# 1. Write a blog post #
########################
print('[1] 글 쓰는 중...')

content = notion_ai.blog_post(f'write a blog about {TOPIC}').strip()

title = content.split('\n')[0].replace('#', '').strip()

print(f'[*] 제목: {title}')

translation = translator.translate(title)
print(f'[*] 영문 제목: {translation}')

#######################
# 2. Generate a image #
#######################
print('[2] 이미지 생성하는 중...')

res_img = openai.Image.create(
    prompt=translation,
    n=1,
    size='512x512'
)

img_url = res_img['data'][0]['url']
img_path = f'imgs/{TOPIC}.png'

urllib.request.urlretrieve(img_url, img_path)

#######################
## 3. Upload a image ##
#######################
print('[3] 이미지 업로드 하는 중...')

files = {'uploadedfile': open(img_path, 'rb')}
params = {'access_token': ACCESS_TOKEN, 'blogName': ts.blog_name, 'targetUrl': BLOG_URL, 'output':'json'}
res_upload = requests.post('https://www.tistory.com/apis/post/attach', params=params, files=files)

replacer = res_upload.json()['tistory']['replacer']

#######################
# 4. Write a new post #
#######################
print('[4] 포스팅 업로드 하는 중...')

content = f"""
<p>{replacer}</p>

{content}
"""

html = markdown.markdown(content)

res_post = ts.write_post(
    title=title,
    content=html,
    visibility='3',         # 발행상태 (0: 비공개 - 기본값, 1: 보호, 3: 발행)
    acceptComment='1')      # 댓글 허용 (0, 1 - 기본값)

print(f"[*] 포스팅 완료! {res_post['tistory']['url']}")
