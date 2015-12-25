var defaults = {
  // State machine -- where are we in the submission process?
  ready: false,
  submitted: false,
  done: false,

  // Individual data that we have collected from a variety of widgets.
  userTitle: "", // Title of the user's work.
  userText: "",  // Text of the user's work, as an array.
  mixin: "",     // Mixin selection.

  // End result of the calculation.
  result: ""
};
_.each(defaults, function (v, k) {
  Session.setDefault(k, v);
});
restoreDefaults = function () {
  _.each(defaults, function (v, k) {
    Session.set(k, v);
  });
};
