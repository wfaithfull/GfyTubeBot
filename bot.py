import praw
import OAuth2Util
import re
from time import sleep
from urllib.request import urlopen
from urllib.parse import urlencode
import json

def find(pattern, comment):
    m = re.search(pattern, comment)
    if m is None:
        return (False, '')
    else:
        return (True, m.group())

def make_gfy(youtube_url, hours, minutes, seconds, length):
    url_params = urlencode({'fetchUrl':youtube_url, 'fetchHours':hours, 'fetchMinutes':minutes, 'fetchSeconds':seconds, 'fetchLength':length})
    response = urlopen('https://upload.gfycat.com/transcodeRelease/GfyTubeBot?' + url_params)
    json_response = json.loads(response.read().decode('utf-8'))
    return 'http://gfycat.com/' + json_response['gfyName']

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

                print(haveUrl, haveTime, haveSecs)

                if haveUrl and haveTime and haveSecs:
                    t = time.split(':')
                    gfyUrl = make_gfy(url, t[0], t[1], t[2], secs);
                    print('Gfy created! ' + gfyUrl)
                    mention.reply('[Here\'s your Gfy](' + gfyUrl + ')')
            except praw.errors.RateLimitExceeded as e:
                log(e)
                sleep(e.sleep_time)
            except praw.errors.HTTPException as e:
                if '403' in str(e):
                    log('Encountered 403 forbidden. No point continuing. "{error}"'.format(error=e))
                    return
            except praw.errors.APIException as e:
                log(e)
            except SocketError as e:
                log(e)
            finally:
                mention.mark_as_read()

        sleep(10)
        
if __name__ == "__main__":
    main()