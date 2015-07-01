$(function() {
  var numDisplay = 3;
  if ($(window).width() < 480) {
    $("[data-lightbox]").removeAttr("data-lightbox");
    //uncomment when the site becomes responsive
    //numDisplay = 2;
  }
  if ($(window).width() < 350) {
    //uncomment when the site becomes responsive
    //numDisplay = 1;
  }
  $(".photoset").each(function() {
    if ($(this).find("li").length > 2) {
      $(this).find("ul").addClass("ts-list");
      $(this).thumbScroller({
	      responsive:true,
	      numDisplay:numDisplay,
	      slideWidth:200,
	      slideHeight:200,
	      slideMargin:5,
	      slideBorder:2,
	      padding:10,
	      navButtons:'hover',
	      playButton:false,
	      continuous:true,
      });
    }
  });
  //$('a').bind('touchend', function(e) {
  //  $(this).click();
  //});
});

function createCookie(name,value,days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
  }
  else var expires = "";
  document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

function eraseCookie(name) { createCookie(name,"",-1); }

function openCart() {
  $("body").append("<cart></cart>");
  riot.mount("cart");
}

function updateCartButton() {
  var total = 0,quantity=0;
  PRODUCTS.list.forEach(function(l) {
    total += l.price*l.quantity;
    quantity += l.quantity;
  });
  var button = $(".store-button").hide();
  button.find(".quantity").html(quantity);
  button.find(".total").html("$"+total.toFixed(2));
  if (total) { button.show(); }
}