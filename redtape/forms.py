from django import forms
from django.core.files import File
from django.template.defaultfilters import slugify

from .models import Signature, Document

from jsignature.forms import JSignatureField
import json

class SignatureForm(forms.ModelForm):
  document = forms.ModelChoiceField(Document.objects.all(),widget=forms.HiddenInput())
  signature = JSignatureField(label="Sign Your Name")
  def __init__(self, *args, **kwargs):
    self.document = kwargs.pop('document')
    super(SignatureForm, self).__init__(*args, **kwargs)
    self.fields.pop('document')
    # generate extra fields
    self.extra_fields = []
    for field in self.document.fields_json:
      if field['type'] == 'header':
        continue
      self.extra_fields.append(field['slug'])
      if field['type'] == 'select':
        choices = field['choices']
        if not field['required']:
          choices = [('',[('','No Response')])] + choices
        self.fields[field['slug']] = forms.ChoiceField(required=field['required'],choices=choices)
      else:
        self.fields[field['slug']] = forms.CharField(required=field['required'])
    if not self.document.signature_required:
      self.fields.pop('date_typed')
      self.fields.pop('name_typed')
      self.fields.pop('signature')
    else:
      # put signature fields at the end
      self.fields['date_typed'] = self.fields.pop('date_typed')
      self.fields['name_typed'] = self.fields.pop('name_typed')
      self.fields['signature'] = self.fields.pop('signature')
      
  def save(self,*args,**kwargs):
    commit = kwargs.pop("commit",True)
    kwargs['commit'] = False
    instance = super(SignatureForm,self).save(*args,**kwargs)
    instance.data = json.dumps({f:self.cleaned_data.get(f,None) for f in self.extra_fields})
    instance.document = self.document
    if commit:
      instance.save()
    return instance
  class Meta:
    model = Signature
    fields = ('date_typed','name_typed','signature')
