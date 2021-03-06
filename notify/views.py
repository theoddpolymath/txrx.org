from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from course.models import Course
from membership.utils import limited_login_required
from .models import NotifyCourse

from lablackey.utils import FORBIDDEN

@login_required
def notify_course(request,course_id):
  course = get_object_or_404(Course,pk=course_id)
  _, new = NotifyCourse.objects.get_or_create(user=request.user,course=course)
  messages.success(request,"You will be emailed next time we teach {}".format(course))
  return HttpResponseRedirect(course.get_absolute_url())

@limited_login_required
def clear_notification(request,model_string,user_id,model_id):
  #! TODO: generalize
  model = NotifyCourse
  obj = get_object_or_404(model,pk=model_id,user=request.limited_user)
  course = obj.course
  obj.delete()
  values = {
    'course': course,
    }
  messages.success(request,"You will not be emailed the next time we teach {}".format(course))
  return HttpResponseRedirect(request.GET.get('next',course.get_absolute_url()))

@limited_login_required
def unsubscribe(request,attr,user_id):
  if not str(request.limited_user.id) == user_id:
    return FORBIDDEN
  if attr == 'notify_course':
    NotifyCourse.objects.filter(user=request.limited_user).delete()
  else:
    usermembership = request.limited_user.usermembership
    setattr(usermembership,"notify_"+attr,False)
    usermembership.save()
  return TemplateResponse(request,'notify/unsubscribe.html',{'attr':attr})
