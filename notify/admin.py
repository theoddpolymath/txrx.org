from django.contrib import admin

from lablackey.db.admin import RawMixin
from .models import NotifyCourse

class NotifyCourseAdmin(RawMixin,admin.ModelAdmin):
  list_display = ("__unicode__","_enrolled")
  raw_id_fields = ("user","course")
  def _enrolled(self,obj):
    return obj.user.enrollment_set.filter(session__course=obj.course).count()

admin.site.register(NotifyCourse,NotifyCourseAdmin)
