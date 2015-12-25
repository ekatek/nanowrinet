// Overall outline helpers
Template.outline.helpers({
  pageTitle: function () {
    return (Session.get('done') && Session.get('userTitle')) || Algorithm.label;
  },
  done: function () {
    return Session.get('done');
  }
});


// Back button
Template.showText.events({
  'click .goback': function () {
    restoreDefaults();
   }
});
