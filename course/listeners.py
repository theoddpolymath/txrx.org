from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from django.dispatch import receiver
from django.http import QueryDict
from django.conf import settings
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string

from notify.models import NotifyCourse
from .utils import get_or_create_student
from lablackey.utils import latin1_to_ascii

import traceback

#! TODO this needs to be moved to store.listeners
def handle_successful_store_payment(sender, user):
  from drop.models import Product, Order, OrderPayment, Cart
  params = QueryDict(latin1_to_ascii(sender.query))
  try:
    order = Order.objects.get(pk=params['invoice'])
  except Order.DoesNotExist:
    mail_admins("missing invoice for %s"%sender.txn_id,"")
    return
  if order.status == Order.PAID:
    #order has already been paid, transaction was repeated. PayPal does this a lot
    return
  total = 0
  if not "num_cart_items" in params:
    mail_admins("No cart items found for %s"%sender.txn_id,"")
    return
  item_count = int(params['num_cart_items'])
  products = []
  for i in range(1,item_count+1):
    total += int(float(params['mc_gross_%d'%i]))
    quantity = int(params['quantity%s'%i])
    try:
      product = Product.objects.get(pk=params['item_number%d'%i] or 0)
    except Product.DoesNotExist:
      mail_admins("Product fail for %s"%sender.txn_id,"")
      continue
    if hasattr(product,"purchase"):
      product.purchase(order.user or user,quantity)
    products.append(product)
  order.status = Order.PAID
  order.user = order.user or user
  order.save()
  payment = OrderPayment.objects.create(
    order=order,
    amount=total,
    payment_method='PayPal',
    transaction_id=sender.txn_id
  )
  [p.save() for p in products] #save decreased stock last, incase of error
  try:
    Cart.objects.get(pk=order.cart_pk).delete()
  except Cart.DoesNotExist:
    pass

_duid2='course.listners.handle_successful_payment'
@receiver(payment_was_successful, dispatch_uid=_duid2)
def handle_successful_payment(sender, **kwargs):
  from course.models import Enrollment, Session, reset_classes_json

  # these two errors occurred because of the donate button on the front page.
  # they can be removed by checking for that
  if not sender.txn_type == "cart":
    # handled by membership.listeners
    return
  params = QueryDict(sender.query)
  _uid = str(params.get('custom',None))
  user,new_user = get_or_create_student(params)
  user.active = True
  user.save()
  if params.get('invoice',None):
    return handle_successful_store_payment(sender,user)
  if not "num_cart_items" in params:
    mail_admins("No cart items found for %s"%sender.txn_id,"")
    return
  item_count = int(params['num_cart_items'])

  enrollments = []
  error_sessions = []
  fails = []
  for i in range(1, item_count+1):
    pp_amount = float(params['mc_gross_%d'%i])
    quantity = int(params['quantity%s'%i])

    try:
      session = Session.objects.get(id=int(params['item_number%d' % (i, )]))
    except Session.DoesNotExist:
      fails.append(("Session not found",traceback.format_exc()))
      continue
    except ValueError:
      fails.append(("Non-integer session number",traceback.format_exc()))
      continue

    enrollment,new = Enrollment.objects.get_or_create(user=user, session=session)
    if enrollment.transaction_ids and (sender.txn_id in enrollment.transaction_ids):
      fails.append(("Multiple transaction ids blocked for enrollment #%s"%enrollment.id,""))
      continue
    enrollment.transaction_ids = (enrollment.transaction_ids or "") + sender.txn_id + "|"
    NotifyCourse.objects.filter(user=user,course=session.course).delete()
    if new:
      enrollment.quantity = quantity
    else:
      enrollment.quantity += quantity
    enrollment.save()
    enrollments.append(enrollment)
    price_multiplier = (100-user.level.discount_percentage) / 100.
    # We're ignoring people who overpay since this happens when a member doesn't login (no discount)
    if pp_amount < price_multiplier*session.course.fee * int(quantity):
      l = [
        "PP cost: %s"%pp_amount,
        "Expected Cost: %s"%(price_multiplier*session.course.fee * int(quantity)),
        "discount: %s"%user.level.discount_percentage,
        "Session Fee: %s"%session.course.fee,
        "Session Id: %s"%session.id,
        "Quantity: %s"%enrollment.quantity,
        "PP Email: %s"%sender.payer_email,
        "U Email: %s"%user.email,
        "u_id: %s"%_uid, #if this is none they won't get a discount
      ]
      error_sessions.append("\n".join(l))
    if enrollment.session.total_students > enrollment.session.course.max_students:
      s = "Session #%s overfilled. Please see https://txrxlabs.org/admin/course/session/%s/"
      mail_admins("My Course over floweth",s%(enrollment.session.pk,enrollment.session.pk))

  if fails:
    body = "=======\n\n".join(["%s\n%s\n\n"%(s,b) for s,b in fails])
    mail_admins("%s fails in purchasing process"%len(fails),body)
  values = {
    'enrollments': enrollments,
    'user': user,
    'new_user': new_user,
    'settings': settings
  }
  if enrollments:
    body = render_to_string("email/course_enrollment.html",values)
    subject = "Course enrollment confirmation"
    send_mail(subject,body,settings.DEFAULT_FROM_EMAIL,[user.email])
  if error_sessions:
    mail_admins("Enrollment Error","\n\n".join(error_sessions))
  reset_classes_json("classes reset during course enrollment")

@receiver(payment_was_flagged, dispatch_uid='course.signals.handle_flagged_payment')
def handle_flagged_payment(sender, **kwargs):
  handle_successful_payment(sender, **kwargs)
