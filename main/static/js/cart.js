function loadJSON(url) { window.location = url; } // IE Fallback
function showLogin() {
  $("#login-dialog").toggleClass("login-visible");
}

simpleCart.successURL = window.location.origin+"/classes/?success";
simpleCart.email = window.SHOP.email;
function showCart() {
  $("#cart-modal").modal({width: 400, modal: true, minHight: 300});
}

function addClass(session) {
  addItem(session.name,session.fee,session.id);
  toggleCourses(session.name);
  $("#cartModal").modal({show:true})
}

function addItem(name,price,id) {
  simpleCart.add('name='+name,'price='+price,'id='+id,'quantity=1');
}

function toggleCourses(name) {
  $(".in-cart").removeClass("in-cart");
  var has_items = false;
  $("#cartEmpty").show();
  for (id in simpleCart.items) {
    if ($("#s"+id).length) {
      $("#s"+id).addClass("in-cart");
    }
    $("#cartEmpty").hide();
    has_items = true;
  }
  simpleCart.update();
  if (has_items) { $("#mobileCart,nav .btn-cart").show(); }
  else { $("#mobileCart,nav .btn-cart").hide(); }
  $(".recentAdd").removeClass("recentAdd");
  $(".itemContainer").each(function() {
    if ($(this).find(".itemName").text() == name) {
      $(this).addClass("recentAdd");
    }
  });
  riot.update('*');
}

function applyFilters(that) {
  // Controls filters found in widgets/filters.html and course/_filters.html
  var form = $(that);
  var data = form.serializeArray();
  var items = $(".filterable").show();
  if ($("#show_closed").attr("checked")) { $(".course_list .past").show(); }
  else { $(".course_list .past").hide(); }
  for (var i=0; i<data.length;i++) {
    var name = data[i].name;
    var value = data[i].value;
    if (!value) { continue }
    items.filter(function() {
      return $(this).data(name).search(value)<0;
    }).hide();
  }
}

function startCheckout() {
  var data = [];
  var cart_items = simpleCart.items;
  for (id in cart_items) {
    data.push({pk: id, quantity: cart_items[id].quantity})
  }
  $.get(
    "/classes/start_checkout/",
    {"cart": JSON.stringify(data)},
    function (data) { verifyCheckout(data); },
    "json"
  )
}

function verifyCheckout(data) {
  if (window.location.search.indexOf("overbook") != -1 || (data.length == 0)) {
    createCookie("checkout_initiated","yes!",10);
    simpleCart.checkout();
    return;
  }
  var msg = "Sorry, some of the classes you're trying to take have filled since you first loaded this page."
  msg += "\nThe following have been removed from your cart:"
  for (var i=0; i < data.length; i++) {
    var cart_item = simpleCart.items[data[i].pk]
    var item_name = cart_item.name.replace(/<(?:.|\n)*?>/gm, '');
    msg += "\n\n"+item_name+" "
    if (data[i].remaining > 1) {
      msg += "("+ data[i].remaining+ " slots remaining)"
    } else if (data[i].remaining == 1) {
      msg += "(1 slot remaining)"
    } else {
      msg += "(class full)"
    }
    cart_item.remove();
  }
  alert(msg);
}

$(document).ajaxError(function() {
  if (!window.IGNORE_AJAX_ERRORS) {
    alert("An unknown error has occurred. Please try again or email us at classes@txrxlabs.org")
  }
});

$(function() {
  $('[data-toggle="tab"]').click(function(e) {
    var $this = $(this), loadurl = $this.data('href'), targ = $($this.attr('href'));
    if (!loadurl) { return true; }

    $this.removeData('href');

    if (targ.hasClass("needs_ajax")) {
      $.get(loadurl, function(data) {
        targ.html(data).removeClass("needs_ajax");
      });
    }
  });
});

function simple_cart_ready() {
  for (id in simpleCart.items) {
    uR.forEach(uR.drop.products_list,function(product) {
      if (product.session_id == id) { uR.drop.saveCartItem(product.id,simpleCart.items[id].quantity); }
    });
  }
  simpleCart.empty();
};
uR.drop.ready(function() { simpleCart.ready(simple_cart_ready); })
