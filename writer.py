#!./venv/bin/python3

from openai import OpenAI
import requests
import json
import jwt
import random
import tempfile
import os
import sys
import io
import fortune
from datetime import datetime as dt
from io import BytesIO
from unsplash.api import Api
from unsplash.auth import Auth



client = OpenAI(
    base_url="http://localhost:8000",  # "http://<api-server IP>:port"
    api_key="sk-no-key-required"
)  # openai client instance

settings = json.loads(open('settings.json', 'r').read())

# Unsplash API keys
unsplash_access_key = settings["unsplash_access_key"]  # this is Access Key from your app's settings in your Unsplash profile (I also wrote this in README)
unsplash_secret_key = settings["unsplash_secret_key"]  # this is Secret key from your app's settings in your Unsplash profile
unsplash_redirect_uri = "urn:ietf:wg:oauth:2.0:oob"  # this is Redirect URI from Redirect URI & Permissions section

# Ghost API keys
ghost_instance_name = settings["ghost_instance_name"]  # you can name it how do you like
ghost_url = settings["ghost_url"]  # this is URL of your Ghost website
ghost_admin_api_key = settings["ghost_admin_api_key"]  # keys from 'Integrations' tab in settings of your Ghost admin

# prompts for LLM
article_name = ""  # fortune output - the name of the future article
old_stdout = sys.stdout
sys.stdout = buffer = io.StringIO()

sys.argv.append('-s')  # adding arguments for using fortune with '-s' flag (short adage)
try:
    fortune.main()
except SystemExit:
    pass

sys.stdout = old_stdout
words = buffer.getvalue().split()

if '--' in words:
    index = 0
    for i in range(len(words) - 1, -1, -1):
        if words[i] == '--':
            index = words.index('--')
            break
    if words[0][0] != '"' and words[0][0] != "'":
        words[0] = '"' + words[0]
        words[index - 1] += '"'
    words[index] = '-'
article_name = ' '.join(words) + '\n'

prompt_text = f"Generate one long news article without a title, based on the following sentence:{article_name}"  # prompt for generating news article in markdown
prompt_unsplash = 'reduce this sentence to four words'  # prompt for generating query for image search using name of the article
prompt_tag = 'generate one news category for this news article in one word'  # prompt for generating news category
words_check = ['[','lorem', '<', '|']  # forbidden words  -> this helps to find articles that don't contain stuff like [author's name], 'lorem ipsum...' etc.
min_symbols = 500  # minimum number of symbols that answer from AI should contain


class GhostAdmin:
    def __init__(self, site_name):
        self.siteName = site_name
        self.site = None
        self.set_site_data()
        self.token = None
        self.headers = None
        self.create_headers()

    def set_site_data(self):
        sites = [{'name': ghost_instance_name, 'url': ghost_url, 'ghost_admin_api_key': ghost_admin_api_key}]
        self.site = next((site for site in sites if site['name'] == self.siteName), None)

        return

    def create_token(self):  # creating short-lived single-use JSON Web Tokens. The lifespan of a token has a maximum of 5 minute. You can read more about it: https://ghost.org/docs/admin-api/#token-authentication
        key = self.site['ghost_admin_api_key']
        kid, secret = key.split(':')
        iat = int(dt.now().timestamp())
        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': kid}
        payload = {'iat': iat, 'exp': iat + (5 * 60), 'aud': '/v3/admin/'}
        self.token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

        return self.token

    def create_headers(self):
        if self.site is not None:
            self.create_token()
            self.headers = {'Authorization': 'Ghost {}'.format(self.token)}

        return self.headers

    def create_post(self, title, body, body_format='html', excerpt=None, tags=None, authors=None, status='draft',
                    featured=False, feature_image=None, slug=None):
        content = {'title': title}
        if body_format == 'markdown':
            content['mobiledoc'] = json.dumps({'version': '0.3.1', 'markups': [], 'atoms': [],'sections': [[10, 0]],
                                               'cards': [['markdown', {'cardName': 'markdown', 'markdown': body}]]})
        else:
            content['html'] = body
        if excerpt is not None:
            content['custom_excerpt'] = excerpt
        if tags is not None:
            content['tags'] = tags
        if authors is not None:
            content['authors'] = authors
        content['status'] = status
        content['featured'] = featured
        if feature_image is not None:
            content['feature_image'] = self.site['url'] + feature_image
        if slug is not None:
            content['slug'] = slug

        url = self.site['url'] + 'ghost/api/v3/admin/posts/'
        params = {'source': 'html'}
        result = requests.post(url, params=params, json={"posts": [content]}, headers=self.headers)

        if not result.ok:
            sys.exit('error: post not created (status_code:' + str(result.status_code) + ')' + str(result.reason))

        print('Success: post created (status_code:' + str(result.status_code) + ')')
        return


    def load_image(self, image_path_and_name):  # creating imageObject for imageUpload function
        try:
            image = open(image_path_and_name, 'rb')
            image_object = image.read()
            image.close()
            image = BytesIO(image_object)
            return image

        except Exception as e:
            sys.exit(f"An error while loadImage function occurred: {e}")


    def image_upload(self, image_name, image_object):  # uploading image to ghost
        url = self.site['url'] + 'ghost/api/v3/admin/images/upload/'
        files = {"file": (image_name, image_object, 'image/jpeg')}
        params = {'purpose': 'image', 'ref': image_name}  # 'image', 'profile_image', 'icon'
        result = requests.post(url, files=files, params=params, headers=self.headers)

        return result


def download_image_by_id(photo_id, filename):  # downloading concrete image from Unsplash site using image ID
    # API endpoint for a specific photo based on ID
    url = f"https://api.unsplash.com/photos/{photo_id}?client_id={unsplash_access_key}"

    # Make a GET request to the Unsplash API for the specific photo
    response = requests.get(url)

    if response.status_code == 200:
        # Extract image URL from the response
        image_url = response.json()['urls']['full']

        # Make a GET request to download the image
        image_response = requests.get(image_url, stream=True)
        # Save the image to a file
        if image_response.status_code == 200:
            with open(filename, 'wb') as file:
                image_response.raw.decode_content = True
                file.write(image_response.content)

        else:
            sys.exit("Failed to download image")

    else:
        sys.exit("Failed to fetch photo details from Unsplash")


def answer_from_ai(query: str):  # sending question to model
    response = client.chat.completions.create(
        model="",
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content.replace('<|im_end|>', '')


def unsplash_image_search(query: str):  # sending request for searching picture to Unsplash site
    auth = Auth(unsplash_access_key, unsplash_secret_key, unsplash_redirect_uri)
    api = Api(auth)
    photo_id = ''

    while photo_id == '':  # check, if the photo has been used before
        res = api.photo.random(query=query, orientation='landscape')
        photo_id = res[0].id

        with open('photo_ids_db', 'r') as f:
            ids = f.read().split()
            if photo_id in ids:
                photo_id = ''

    with open('photo_ids_db', 'a') as f:
        f.write(photo_id + '\n')


    return photo_id


def create_temp_directory():  # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    return temp_dir


def delete_all_files_from_temp(temp_dir):
    try:
        # Delete all files in the temporary directory
        for file_name in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file_name)
            os.remove(file_path)

    except Exception as e:
        sys.exit(f"An exception occurred: {e}")


# GENERATING THE NEWS ARTICLE
if __name__ == '__main__':
    generated_body = answer_from_ai(prompt_text)
    generated_text = '# ' + article_name + generated_body

    if len(generated_text) < min_symbols:  # CHECKING FOR VALID AI RESPONSE
        sys.exit(f'sorry, very short AI response (less than {min_symbols} symbols)')

    ignore_case_text = generated_text.lower()
    for word in words_check:
        if word in ignore_case_text:
            sys.exit(f'sorry, bad AI response (output contains forbidden word: {word}), try again')


    excerpt = str(generated_body[:generated_body.find('.')])

    # GENERATING QUERY FOR UNSPLASH API
    query = answer_from_ai(prompt_unsplash + article_name)
    photo_id = unsplash_image_search(query)

    image_name = f'{random.randint(0, 999)}.jpg'  # File name to save the downloaded photo
    temp_dir = create_temp_directory()
    output_filename = temp_dir + image_name
    download_image_by_id(photo_id, output_filename)

    # GENERATING TAGS
    tag = answer_from_ai(prompt_tag + generated_body)

    post_tags = [{'name': tag}]

    ga = GhostAdmin(ghost_instance_name)  # your Ghost instance
    image_object = ga.load_image(output_filename)  # loading image to Ghost
    result = ga.image_upload(image_name=image_name, image_object=image_object)

    num_attempts = 0  # checking for result's validity


    while num_attempts <= 3 and (result.status_code >= 500 or result.ok):
        # if it is server error, try again 3 times (if response is not error, continue)
        num_attempts += 1

        if result.ok:
            image_url = json.loads(result.text)['images'][0]['url']  # image_url on Ghost server
            result = 'success: ' + image_url

            img_idx = image_url.find('content')
            image_slug = image_url[img_idx:]
            # for POST request that creates a post, image URL should be like:
            # content/images/year/month/image.jpg, so we should get rid of other words in URL

            ga.create_post(title=article_name, body_format='markdown', excerpt=excerpt, feature_image=image_slug,
                                         tags=post_tags, body=generated_body, status='published')

            delete_all_files_from_temp(temp_dir)
            quit()
        else:
            result = ga.image_upload(image_name=image_name, image_object=image_object)

    delete_all_files_from_temp(temp_dir)
    if result.status_code >= 500:
        sys.exit(f'Unsplash server error.')
    else:
        sys.exit('error: image upload failed (' + str(result.status_code) + ')' + str(result.reason))
