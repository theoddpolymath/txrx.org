from django.db.models import Q
from rest_framework import serializers

from .models import User
from tool.models import UserCriterion
from api.serializers import BaseSizzler

class SearchSizzler(BaseSizzler):
  permissions = classmethod(lambda class_,request: request.user.is_staff)
  @classmethod
  def get_queryset(class_,request):
    q = request.REQUEST.get('q',None)
    qs = class_.Meta.model.objects.all()
    if q:
      _Q = Q()
      for f in ['username','email','usermembership__paypal_email','rfid','first_name','last_name']:
        _Q = _Q | Q(**{f+"__icontains":q})
      qs = qs.filter(_Q).filter(is_active=True).distinct()
    return qs
  class Meta:
    model = User
    fields = ('username','pk','email','paypal_email','get_full_name','criterion_ids')