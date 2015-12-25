// Author mixins.
Template.mixin.helpers({
  mixins: function () {
    return Algorithm.Mixins.find({}, {sort: {_id: 1}});
  },
  checked: function () {
    return Session.get('mixin') === this.letter ? "select" : "";
  },
  authorAndTitle: function () {
    if (this.author === "") {
      return "None, please!";
    }
    return this.author + " (" + this.title + ")";
  }
});
Template.mixin.events({
  'click .selection': function (e) {
     Session.set('mixin', this.letter);
  }
});


// File upload. We used to check if the input is actually valid, but it is not
// really worth the effort, since most of our backend components are resillient
// to it and we don't really get a lot of malicious traffic.
//
// XXX: If this was a real webapp, we would really care about scanning for
// unresonable input files.
Template.upload.events({
  'change #upload': function (e) {
       var reader = new FileReader();
       reader.onload = function() {
         var text = this.result;
         if (! text) { return; }
         var blank = new RegExp(" |\n|\t");
         text = text.split(blank);
         Session.set('userText', text);
       };
       reader.readAsText(e.target.files[0]);
   }
});

Template.upload.created = function () {
  this.invalidInput  = new ReactiveVar(false);
};

Template.upload.helpers({
  'invalid': function () {
    return Template.instance().invalidInput.get();
  },
  'lastWords': function () {
    var last  = _.last(Session.get("userText"), 10).join(" ");
    if (last.length > 200) {
      // Something is wrong! We do this check, because otherwise, our rendering is off.
      Session.set('userText', "");
      Template.instance().invalidInput.set(true);
    }
    this.invalidInput  = new ReactiveVar(false);
    return last;
  },
  'wordcount': function () {
    return Session.get("userText").length;
   }
});

// Get the user title. This is a pretty straightforward user input box. It never
// goes to the server, we don't really care about having a lot in the way of
// validation here.
Template.usertitle.events({
  'keyup #usertitle': function (e) {
    var title = document.getElementById('usertitle').value;
    Session.set('userTitle', title);
  }
});
Template.usertitle.helpers({
  "usertitle": function (e) {
    return Session.get('userTitle');
  }
});

// If the user has filled out all the mandatory fields, then we are ready to
// submit data over the wire.
Tracker.autorun(function () {
  Session.set('ready', (Session.get('userText') && Session.get('mixin')));
});



// The big computation button template.
Template.tryit.created = function () {
  this.timer  = new ReactiveVar(0);
  this.timerInterval  = new ReactiveVar("");
};

Template.tryit.helpers({
  ready: function () {
    return Session.get('ready') ? "button-ready" : "button-not-ready";
  },
  waiting: function () {
    return Session.get('submitted');
  },
  timer: function () {
    return Template.instance().timer.get();
  }
});

Template.tryit.events({
  'click .button-ready': function () {
    if (!(Session.get('ready'))) { return; };
    var myTemplate = Template.instance();
    var request = {
      mixin: Session.get('mixin'),
      text: Session.get('userText')
    };
    Meteor.call(Algorithm.method, request, function (error, result) {
      if (error) {
        console.log(error);
        result = "<b>Internal error!<br><br>" +
          "Alas. The wheels of internet spin fast.<br>"+
          "This code rotted; infrastructure crashed; <br>" +
          "Were toys not actually built to last? <br>" +
          "Do try again, perhaps the tide will turn... <br><br>";
        result = result + "The error was: </b>" + error.message;
      }
      Session.set('result', result);
      Session.set('done', true);
      Meteor.clearInterval(myTemplate.timerInterval.get());
    });
    Session.set('submitted', true);

    // Start the timer.
    myTemplate.timerInterval.set(Meteor.setInterval(
      function() {
        var timer  = myTemplate.timer.get();
        myTemplate.timer.set(timer + 1);
      }, 1000)
    );
  }
});


// Show result.
Template.result.helpers({
  result: function () {
    return Session.get('result');
   }
});

// Detailed explanation
Template.explanation.helpers({
  details: function () {
    return Algorithm.details;
  }
});
