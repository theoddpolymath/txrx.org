from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from .models import Event, EventOccurrence

import datetime

def index(request):
  pass

def occurrence_detail(request,occurrence_id):
  occurrence = EventOccurrence.objects.get(pk=occurrence_id)
  values = {
    'occurrence': occurrence,
    }
  return TemplateResponse(request,'event/occurrence_detail.html',values)

def repeat_event(request,period,event_id):
  """
  Creates EventOccurrences for an event for one whole year.
  Will delete all upcoming EventOccurrences.
  """
  event = Event.objects.get(pk=event_id)
  occurrences = event.upcoming_occurrences
  start = occurrences[0].start
  end = occurrences[0].end
  occurrences.delete()
  if period == 'weekly':
    days = 7
    message = "This event has been repeated weekly for a year."
  else:
    days = 30
    message = "This event has been repeated every thirty days for a year. Please check for accuracy."
  count = 0
  while count < 365:
    td = datetime.timedelta(count)
    e = EventOccurrence(
      event=event,
      start=start+td,
      )
    if end:
      e.end=end+td
    e.save()
    count += days
  messages.success(request,"All upcoming occurrences have been deleted.")
  messages.success(request,message)
  return HttpResponseRedirect(request.META['HTTP_REFERER'])