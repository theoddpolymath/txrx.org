from django.core.management.base import BaseCommand
from django.conf import settings

from simplejson import loads
import requests, os

from instagram.models import InstagramPhoto,photofile_path

InstagramPhoto.objects.all().delete()

tag_url = "https://api.instagram.com/v1/tags/%s/media/recent?access_token=%s"
user_url = "https://api.instagram.com/v1/users/%s/media/recent?access_token=%s&count=100"
user_search_url = "https://api.instagram.com/v1/users/search?q=%s&access_token=%s"
token = getattr(settings,'INSTAGRAM_TOKEN',"3794301.f59def8.e08bcd8b10614074882b2d1b787e2b6f")

def save_photos(response,new,count,approved=False,username=""):
  photo_dir = os.path.join(settings.MEDIA_ROOT,photofile_path)
  if not os.path.exists(photo_dir):
    os.mkdir(photo_dir)
  for item in response['data']: # image dicts
    defaults = dict(
      created_time = item['created_time'],
      approved = approved
      )
    if item['caption']:
      defaults['username'] = item['caption']['from']['username']
      defaults['caption'] = item['caption']['text']
    else:
      defaults['username'] = username or 'anonymous'
    i,n = InstagramPhoto.objects.get_or_create(iid=item['id'],defaults=defaults)
    new += n; count += 1
    if n: # save photos
      for size in ['thumbnail','low_resolution','standard_resolution']:
        url = item['images'][size]['url']
        ri = requests.get(url,stream=True)
        path = os.path.join(photo_dir,url.split("/")[-1])
        f = open(path,'w')
        f.write(ri.raw.read())
        f.close()
        setattr(i,size,path.split('media/')[-1])
        i.save()
        print "%s written"%url
  return new,count

class Command (BaseCommand):
  def handle(self, *args, **options):
    # InstagramPhoto.objects.all().delete() #useful for testing!
    wxh = lambda img: "%sx%s"%(img['width'],img['height'])
    new,count = 0,0
    tag = getattr(settings,'INSTAGRAM_TAG','')
    userid = getattr(settings,'INSTAGRAM_USERID','')
    username = getattr(settings,'INSTAGRAM_USERNAME','')
    if tag:
      r = requests.get(tag_url%(tag,token))
      response = loads(r.text)
      new,count = save_photos(response,new,count)
    if username and not userid:
      r = requests.get(user_search_url%(username,token))
      response = loads(r.text)
      for user in response['data']:
        if user['username'] == username:
          userid = user['id']
          break
    if userid:
      r = requests.get(user_url%(userid,token))
      response = loads(r.text)
      new,count = save_photos(response,new,count,approved=True,username=username)
    if new:
      pass
    """send_email(
        "INSTAGRAM UPDATE",
        "noreplay@mouthwateringmedia.com",
        "new instagram photos",
        "There are %s new instagram photos. Pleas visit the admin to approve them."%new
        )"""