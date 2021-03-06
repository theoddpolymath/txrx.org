<tool-checkout>
  <div each={ window.TXRX.criteria }>
    <a href="#criterion/{ id }" class="btn btn-block btn-success">{ name }</a>
  </div>

</tool-checkout>

<badge>
  <div class="row">
    <div class="col-sm-4">
      <div class="badge-box">
        <div class="row">
          <div each={ columns } class="col-sm-6">
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

  var self = this;
  this.on("mount",function() {
    self.columns = [{'rows':[]},{'rows':[]}]
    window.TXRX.permissions.forEach(function(p) {
      p.has = (uR.auth.user.permission_ids.indexOf(p.id) > -1);
    });
    window.TXRX.groups.forEach(function(g) {
      self.columns[g.column].rows.push(g);
      g.permissions = window.TXRX.permissions.filter(function(p) {
        if (p.group_id == g.id) {
          if (p.has) { g.any = true }
          return true
        }
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
    <h2><i class="fa fa-check fa-2x" if={ has }></i> { name }</h2>
    <div each={ courses } class="course">
      <i class="fa fa-check fa-2x" if={ has }></i>
      { name }
    </div>
  </div>
  this.course_ids = uR.auth.user.completed_course_ids
  this.on("update",function() {
    if (this.opts.criteria_json) {
      this.opts.criteria_json.forEach(function(criteria) {
        criteria.has = uR.auth.user.criterion_ids.indexOf(criteria.id) != -1;
        criteria.courses.forEach(function(course) {
          course.has = uR.auth.user.completed_course_ids.indexOf(course.id) != -1;
        });
      });
    }
  });
</permission>

<toolmaster>
  <search-users search_term={ opts.search_term }>
    <h2>Manage Tool Permission</h2>
    <p>Search for students to change their privileges and course completions.</p>
  </search-users>
  <div if={ active_user } class="row buttons">
    <div class="col-sm-6">
      <div if={ student.courseenrollment_jsons.length }>
        <h3><u>Course Checkouts</u></h3>
        <checkbox each={ student.courseenrollment_jsons } onclick={ parent.toggleCourseEnrollment } if={ can_change }>
          { course_name }
        </checkbox>
      </div>
      <div if={ student.enrollment_jsons.length }>
        <h3><u>Course Enrollments</u></h3>
        <checkbox each={ student.enrollment_jsons } onclick={ parent.toggleEnrollment } if={ can_change }>
          { session_name }
        </checkbox>
      </div>
      <div if={ student.signature_jsons.length }>
        <h3><u>Document Completions</u></h3>
        <checkbox each={ student.signature_jsons } onclick={ parent.toggleSignature } if={ can_change }>
          { document_name }
        </checkbox>
      </div>
    </div>

    <div class="col-sm-6">
      <h3><u>Tool Criteria</u></h3>
      <checkbox each={ criteria } onclick={ parent.toggleCriterion } if={ can_change }>
        { name }
        <b if={ expires }>EXPIRES: { expires }</b>
      </checkbox>
    </div>
  </div>

  var self = this;
  toggleCriterion(e) {
    toggle(e,{ criterion_id: e.item.id });
  }

  toggleEnrollment(e) {
    toggle(e,{ enrollment_id: e.item.id });
  }
  toggleCourseEnrollment(e) {
    toggle(e,{ courseenrollment_id: e.item.id });
  }
  toggleSignature(e) {
    toggle(e,{ signature_id: e.item.id });
  }

  function toggle(e,d) {
    if (e.item.locked) { return }
    d.user_id = self.active_user.id;
    uR.ajax({
      url: '/tools/toggle_criterion/',
      data: d,
      success: function(data) {
        self.student = data;
        self.update();
      },
      target: self.root.querySelector(".buttons")
    });
  }

  this.on("update", function() {
    self.criteria  = window.TXRX.criteria;
    if (self.active_user) {
      var user = uR.auth.user
      var usercriterion = {};
      uR.forEach(self.student.usercriterion_jsons,function(ucj) { usercriterion[ucj.criterion_id] = ucj });
      self.criteria.forEach(function(c) {
        c.has = usercriterion[c.id];
        c.locked = self.student.locked_criterion_ids.indexOf(c.id) != -1;
        c.expires = c.has && c.has.expires && moment(new Date(c.has.expires)).format("MMMM DD, YYYY");
        c.can_change = user.is_toolmaster || user.master_criterion_ids.indexOf(c.id) != -1;
      });
      self.student.enrollment_jsons.forEach(function(e){
        e.has = e.completed;
        e.can_change = user.is_toolmaster || user.session_ids.indexOf(e.session.id) != -1;
      });
      self.student.courseenrollment_jsons.forEach(function(e) {
        e.has = e.completed;
        e.can_change = user.is_toolmaster;
      });
      self.student.signature_jsons.forEach(function(e) {
        e.locked = true;
        e.can_change = user.is_toolmaster;
      });
    }
  });

  select(e) {
    this.active_user = e.item;
    uR.ajax({
      url: "/api/user/student/"+e.item.id+"/",
      success: function(data) {
        self.student = data;
        self.update()
      },
      target: this.root
    })
  }
</toolmaster>

<set-rfid>
  <search-users if={ !opts.active_id }>
    <h2>Change RFID</h2>
    <p>Find a user and then select them and you will be prompted for a new rfid</p>
  </search-users>
  <button if={ opts.active_id } onclick={ open }
          class="btn btn-{ _user.rfids.length?'success':'danger' }">Set RFIDs</button>
  <modal if={ active_user } cancel={ cancel } rfids={ active_user.rfids } stay_mounted={ true }>
    <h1>Alter RFIDs</h1>
    Swipe card or enter number for { parent.active_user.username }.
    <form onsubmit={ parent.submit }>
      <input type="text" onblur="this.focus()"/>
    </form>
    <div if={ opts.rfids.length }>
      <h3>Delete Current RIFDs</h3>
      <div each={ number,i in opts.rfids } class="alert alert-info">
        { number }
        <a class="pull-right fa fa-close" onclick={ parent.parent.remove }></a>
      </div>
    </div>
    <div if={ parent.error } class="alert alert-danger">{ parent.error }</div>
  </modal>

  var self = this;
  this.on("mount", function() {
    // #! this is so the set-rfid tag can be included into other tags that don't do the searching.
    if (this.opts.active_id) {
      uR.ajax({
        url: "/api/user/search/",
        data: {user_id: this.opts.active_id},
        self: this,
        success: function(data) {
          self._user = data[0];
        },
      });
    }
  });
  open(e) {
    this.active_user = this._user;
    this.update();
    document.querySelector("modal input").focus();
  }
  select(e) {
    this.active_user = e.item;
    this.update();
    document.querySelector("modal input").focus();
  }
  cancel(e) {
    this.active_user = this.old_rfid = this.new_rfid = this.username = null;
    this.update();
  }
  this.on("update",function() {
    this.tags && this.tags.modal.update()
  });
  submit(e) {
    var input = this.root.querySelector("modal input");
    var number = input.value;
    input.value = "";
    uR.ajax({
      url: '/api/change_rfid/',
      data: {'user_id':this.active_user.id,'rfid':number},
      self: this,
      success: function(data) {
        self.active_user.rfids = data.rfids;
        self.error = data.error;
      },
      error: function() { alert("An unknown error occurred. Please contact Chris.") },
      target: self.root.querySelector("modal .inner")
    });
    return false;
  }
  remove(e) {
    uR.ajax({
      url: '/api/remove_rfid/',
      data: {'user_id':self.active_user.id,'rfid':e.item.number},
      self: this,
      success: function(data) { self.active_user.rfids = data.rfids; },
      target: self.root.querySelector("modal .inner")
    });
  }
</set-rfid>

<search-users>
  <yield/>
  <input type="text" name="q" onkeyup={ search } placeholder="Search by name or email" autocomplete="off"
         if={ !parent.active_user }/>
  <div class="results">
    <button class="btn btn-link" onclick={ back } if={ parent.active_user }>
      &laquo; Back to results
    </button>
    <div each={ results } if={ !parent.parent.active_user }>
      <div class="card well" onclick={ parent.parent.select } style="cursor: pointer;">
        <div class="row card-content">
          <div class="col-sm-4 col s4">{ username }<br />{ get_full_name }&nbsp;</div>
          <div class="col-sm-8 col s8">{ email }<br/>{ paypal_email }</div>
        </div>
      </div>
    </div>
    <div if={ !results.length }>
      No results. Try changing query
    </div>
  </div>

  var self = this;
  self._results = [];
  var old_value = '',value;
  search(e) {
    value = self.root.querySelector("[name=q]").value;
    if (old_value == value) { return }
    old_value = value;
    if (!value || value.length < 3) {
      self._results = [];
      self.update();
      return;
    }
    uR.ajax({
      url: "/api/user/search/",
      data: {q: value, empty: self.opts.empty},
      success: function(data) {
        self._results = data;
        self.update()
      },
      target: self.root.querySelector(".results")
    })
  }
  this.search = uR.debounce(this.search);
  back(e) {
    this.parent.active_user = undefined;
    this.parent.back && this.parent.back(e);
    this.parent.update();
  }
  this.on("mount",function() {
    self.root.querySelector("[name=q]").focus();
    self.root.querySelector("[name=q]").value = self.opts.value || "";
    self.search();
  });
  this.on("update",function() {
    if (this.parent.active_user) { this.results = [this.parent.active_user ] }
    else { this.results = this._results }
  });
</search-users>

<checkbox>
  <a class="alert alert-block alert-{ alert_class }">
    <i class="fa fa-{ 'check-': has }square-o fa-2x" if={ !locked }></i>
    <i class="fa fa-lock fa-2x" if={ locked }></i>
    <yield/>
  </a>

  this.on("update",function() {
    if (this.locked) {
      this.icon = "lock";
      this.alert_class = "warning";
    } else {
      this.alert_class = this.has?"success":"danger";
      this.icon = this.has?"check-square-o":"square-o";
    }
  });

</checkbox>
