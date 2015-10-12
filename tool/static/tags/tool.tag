<tool-checkout>
  <div each={ permissions }>
    <div each={ criteria }>
      { name }
    </div>
  </div>

  this.permissions = window.TXRX.permissions;

</tool-checkout>

<badge>
  <div class="row">
    <div class="col-sm-4">
      <div class="badge-box">
        <div class="row">
          <div each={ opts.columns } class="col-sm-6">
            <div each={ rows } style="background-color: {this.color}" class="{ group: true, any: any }">
              <a onclick={ parent.parent.loadPermission } each={ permissions }
                 class="{ permission: true, has: has, has_not: !has }">
                { abbreviation }
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="col-sm-8">
      <permission></permission>
    </div>
  </div>

  var that = this;
  this.on("mount",function() {
    this.user = window.TXRX.user;
    this.opts.columns.forEach(function(i) {
      i.rows.forEach(function(i2) {
        i2.permissions.forEach(function(i3) {
          if (that.user.permission_ids.indexOf(i3.id) > -1) { i3.has = i2.any = true; }
        });
      });
    });
    this.update();
  });
  loadPermission(e) {
    riot.mount("permission",e.item);
  }

</badge>

<permission>
  <h1>{ opts.name }</h1>
  <div each={ opts.criteria_json }>
    <h2>{ name }</h2>
    <div each={ courses }>{ name }</div>
  </div>
  
</permission>

<authorize-criterion>
  <div class="row">
    <div class="col-sm-6">
      <h1>{ opts.name }</h1>
      <input type="text" name="q" onkeyup={ search } placeholder="Search by name or email" autocomplete="off" />
      <div if={ results.length; }>
        <authorize-button each={ results }>
      </div>
    </div>
  </div>

  var that = this;
  that.results = [];
  var old_value = '',value;
  search(e) {
    value = document.querySelector("authorize-criterion [name=q]").value;
    if (old_value == value) { return }
    uR.bounce(s,[e]);
    old_value = value;
  }
  function s(e) {
    that.loading = true;
    if (!value) { that.results = []; that.loading = false; return; }
    $.get(
      "/api/user/search/",
      {q: value},
      function(data) {
        that.loading = false;
        that.results = data;
        that.update()
      },
      "json"
    )
  }
  this.on("mount",function() { $("authorize-criterion [name=q]").focus(); })
</authorize-criterion>

<authorize-button>
  <a class="alert alert-block alert-{ alert_class }" click={ toggle }>
    <div class="row">
      <div class="col-xs-2">
        <i class="fa fa-{ 'check-': has }square-o fa-4x"></i>
      </div>
      <div class="col-xs-5">
        { username }<br />
        { full_name }&nbsp;
      </div>
      <div class="col-xs-5">
        { email }<br/>
        { paypal_email }
      </div>
    </div>
  </a>

  var criterion_id = this.parent.opts.id;
  var that = this;
  this.on("update",function() {
    this.has = this.criterion_ids.indexOf(criterion_id) != -1;
    this.alert_class = this.has?"danger":"success";
  });

  toggle (e) {
    this.root.setAttribute("loading","true");
    $.get(
      "/tools/togglecriterion/",
      {user_id: that.pk, has: that.has,criterion_id: criterion_id},
      function(data) {
        this.root.removeAttribute("loading");
        this.criterion_ids = data;
        this.update();
      },
      "json"
    )
  }

</authorize-button>
