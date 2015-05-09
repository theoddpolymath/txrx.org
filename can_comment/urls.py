from django.conf.urls import url, patterns

urlpatterns = patterns(
  'can_comment.views',
  url('^(\d+)/$','detail'),
  url('^test/$','test'),
  url('^list/$','list_comments'),
  url('^post/$','post'),
  url('^edit/(\d+)/$','edit'),
  url('^delete/(\d+)/$','delete'),
  url('^flag/(\d+)/$','flag'),
)
