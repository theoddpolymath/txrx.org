from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import PasswordResetForm

m = "You are not authorized to do this. If you believe this is in error, please email %s"%settings.WEBMASTER

FORBIDDEN = HttpResponseForbidden(m)

def cached_method(target,name=None):
  target.__name__ = name or target.__name__
  if target.__name__ == "<lambda>":
    raise ValueError("Using lambda functions in cached_methods causes __name__ collisions.")
  def wrapper(*args, **kwargs):
    obj = args[0]
    name = '_' + target.__name__

    if not hasattr(obj, name):
      value = target(*args, **kwargs)
      setattr(obj, name, value)

    return getattr(obj, name)
  
  return wrapper

def cached_property(target,name=None):
  return property(cached_method(target,name=name))

def reset_password(user,
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt'):
  form = PasswordResetForm({'email':user.email})
  if form.is_valid():
    form.save(
      subject_template_name=subject_template_name,
      email_template_name=email_template_name)
    
  else:
    print form.errorsform.save(email_template_name=email_template_name)
