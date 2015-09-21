import praw
import OAuth2Util
import re
from time import sleep
from urllib.request import urlopen
from urllib.parse import urlencode
import json
import random
import string

def find(pattern, comment):
    m = re.search(pattern, comment)
    if m is None:
        return (False, '')
    else:
        return (True, m.group())

def make_gfy(youtube_url, hours, minutes, seconds, length):
    url_params = urlencode({'fetchUrl':youtube_url, 'fetchHours':hours, 'fetchMinutes':minutes, 'fetchSeconds':seconds, 'fetchLength':length})
    key = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
    response = urlopen('https://upload.gfycat.com/transcode/{0}?/{1}'.format(key, url_params))
    json_response = json.loads(response.read().decode('utf-8'))
    success = 'gfyName' in json_response
    if success:
        url = 'http://gfycat.com/' + json_response['gfyName']
    else:
        print(json_response)
        if 'error' in json_response:
            url = json_response['error']
        else:
            url = ''
    return (success, url, key)

def main():
    user_agent = ("Youtube to Gfy converter")

    r = praw.Reddit(user_agent = user_agent);
    o = OAuth2Util.OAuth2Util(r)

    while True:
        o.refresh();
        
        for mention in r.get_unread(limit=None):
            try:
                body = mention.body

                if not find(r'\+/u/(?i)GfyTubeBot', body) or not mention.was_comment:
                    continue
                    
                haveUrl, url = find('(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?',body)
                haveTime, time = find('([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-9]|[0-5][0-9]):([0-9]|[0-5][0-9])',body)
                haveSecs, secs = find('(^|[ ])[0-9]{1,}(?!:)',body)

               

                if haveUrl and haveTime and haveSecs:
                    
                    print('Doing {0}\'s bidding...'.format(mention.author.name))
                
                    t = time.split(':')
                    if int(t[2]) > 15 or int(t[2]) < 1:
                        continue
                        
                    success, gfyUrl, key = make_gfy(url, t[0], t[1], t[2], secs);
                    if not success:
                        print('Failed to create gfy')
                        mention.reply('''The gfycat API didn\'t like that :( 
                        
                        > {0}
                        
                        Check [here](https://upload.gfycat.com/status/{1}) for status
                        '''.format(gfyUrl, key))
                    else:
                        mention.reply('[Here\'s your Gfy]({0})'.format(gfyUrl))
            except praw.errors.RateLimitExceeded as e:
                print(e)
                sleep(e.sleep_time)
            except praw.errors.HTTPException as e:
                if '403' in str(e):
                    print('Encountered 403 forbidden. No point continuing. "{error}"'.format(error=e))
                    return
            except praw.errors.APIException as e:
                print(e)
            finally:
                mention.mark_as_read()

        sleep(30)
        
if __name__ == "__main__":
    main()