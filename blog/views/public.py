"""Main blog views"""
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template.response import TemplateResponse

from tagging.models import Tag

from blog.models import Post, Setting
from blog.forms import FeedBackForm

import datetime, difflib

def post_detail(request, username, slug, template_name="post_detail.html"):
  user = get_object_or_404(User, username=username)

  post = get_object_or_404(Post,user=user,slug=slug)

  try:
    user_settings = Setting.objects.get(user=user)
  except:
    user_settings = None

  if post.status == 'draft' and post.user != request.user and not request.user.is_superuser:
    raise Http404

  return TemplateResponse(request, template_name, {
    'username': username,
    'post': post,
    'meta': user.profile.get_meta(),
    'user_settings': user_settings
  })

def post_list(request, username, post_type='published',
        template_name="post_list.html"):
  user = get_object_or_404(User, username=username)

  try:
    user_settings = Setting.objects.get(user=user)
  except Setting.DoesNotExist:
    user_settings = None

  if post_type == 'published':
    post_type = 'posts'
    status_query = Q(status="published")
  else:
    post_type = 'drafts'
    status_query = Q(status="draft")

  posts = Post.objects.filter(
    status_query,
    Q(publish_dt__lte=datetime.datetime.now()) | Q(publish_dt=None),
    user=user,
  )
  posts = posts.order_by('-publish_dt')

  return TemplateResponse(request, template_name, {
    'username': username,
    'posts': posts,
    'post_type': post_type,
    'meta': user.profile.get_meta(),
    'user_settings': user_settings
  })

@login_required
def feedback(request, template_name='feedback.html'):
  """ Send Feed back """
  user = get_object_or_404(User, username=request.user.username)

  form = FeedBackForm(initial={'email': user.email})

  if request.method == 'POST':
    form = FeedBackForm(request.POST)
    if form.is_valid():
      msg = "Thanks for send us feedback. We hope to make the product better."
      messages.info(request, msg, extra_tags='alert-success')

      print dir(form)
      subject = 'Blog feedback from %s' % user.username
      message = '%s (%s), %s' % (
        request.user.username,
        form.cleaned_data['email'],
        form.cleaned_data['comments'],
      )

      mail_admins(subject, message, fail_silently=False)

  return TemplateResponse(request, template_name, {
    'form': form,
  })

def posts_by_tag(request,name):
  tag = get_object_or_404(Tag,name=name)
  items = tag.items.filter(content_type__app_label="blog",content_type__name="post",object_id__isnull=False)
  posts = [item.object for item in items]
  values = {
    "posts": posts,
    "tag": tag,
    }
  return TemplateResponse(request,"blog/posts_by_tag.html",values)

def post_redirect(request,y,m,d,slug):
  date = datetime.datetime.strptime('%s-%s-%s'%(y,m,d),'%Y-%m-%d').date()
  posts = Post.objects.filter(publish_dt__gte=date,publish_dt__lte=date+datetime.timedelta(1))
  if posts.count() == 1: # found it
    post = posts[0]
  elif posts.count() > 2: # ftake closest slug
    lexscore = lambda post: difflib.SequenceMatcher(a=post.slug.lower(),b=slug.lower()).ratio()
    post = sorted(list(posts),key=lexscore)[-1]
  else:
    #mail_admins('unable to find blog post',request.path)
    raise Http404("Unable to find matching blog article.")
  kwargs = {'username': post.user.username,'slug': post.slug}
  return HttpResponseRedirect(reverse('post_detail',kwargs=kwargs))