from django.conf import settings
from django.core.mail import send_mail,mail_admins
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from course.models import ClassTime
from event.models import EventOccurrence
from membership.models import LimitedAccessKey

from lablackey.mail import mail_on_fail, send_template_email

import arrow

class Command(BaseCommand):
  @mail_on_fail
  def handle(self, *args, **options):
    tomorrow = arrow.utcnow().replace(hour=6,days=1).datetime
    next_day = arrow.utcnow().replace(hour=6,days=2).datetime
    class_times = ClassTime.objects.filter(start__gte=tomorrow,start__lte=next_day,emailed__isnull=True)
    class_times = class_times.exclude(session__course__active=False).exclude(session__active=False).distinct()
    if not class_times:
      return
    print "showing classes from %s to %s"%(tomorrow,next_day)
    print "reminding %s class times"%len(class_times)
    instructor_count = 0
    student_count = 0
    sent = []
    for class_time in class_times:
      instructor_count += 1
      instructor = class_time.session.user
      _dict = {
        'user': instructor,
        'la_key': LimitedAccessKey.new(instructor),
        'SITE_URL': settings.SITE_URL,
        'session': class_time.session,
        'class_time': class_time,
      }
      send_template_email("email/teaching_reminder",instructor.email,context=_dict)
      for enrollment in class_time.session.enrollment_set.all():
        student_count += 1
        user = enrollment.user
        _dict = {
          'user': user,
          'la_key': LimitedAccessKey.new(user),
          'SITE_URL': settings.SITE_URL,
          'session': class_time.session,
          'class_time': class_time,
        }
        if user.email in sent:
          continue
        sent.append(user.email)
        send_template_email("email/course_reminder",user.email,context=_dict)
      class_time.emailed = arrow.utcnow().datetime
      class_time.save()
    print "\n\n\nemailed %s instructors and %s students"%(instructor_count,student_count)
