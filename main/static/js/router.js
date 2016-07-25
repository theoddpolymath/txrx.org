(function() {
  function mainMount(html,data) {
    var tag_name = /[\w-]+/g.exec(html)[0];
    document.getElementById("main").innerHTML = "<"+tag_name+">";
    riot.mount(tag_name,data);
  }
  function fromTemplate(template_name,data) {
    riot.compile(
      "/static/templates/"+template_name+".html",
      function(html) {
        mainMount(template_name,data);
      }
    );
  }
  uR._routes = {
    "/(checkin)/": function() { mainMount("checkin-home"); },
    "/(checkout)/": function() { mainMount("tool-checkout"); },
    "/(rooms)/(\d*)": function(path,data) { fromTemplate("room-list",data); },
    "/(toolmaster)/": function(search_term) {
      mainMount("toolmaster",{search_term:search_term});
    },
    "/my-permissions/": function() { mainMount('badge') },
    "/rfid/": function() { mainMount("set-rfid"); },
    "/week-hours/": function() { mainMount("week-hours"); },
    "/needed-sessions/": function() { fromTemplate("needed-sessions"); }
  };
  TXRX.mainMount = mainMount;
})();
