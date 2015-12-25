// Initialize the AWS Lambda object that we will use to make calls to AWS
// Lambda.
AWSInterface = {};
Meteor.startup(function () {
  // If no AWS settings are specified, log and leave (we might not be calling AWS).
  if (! Meteor.settings || ! Meteor.settings.aws ||
      ! Meteor.settings.aws.key || ! Meteor.settings.aws.secret) {
    console.log("Please specify AWS key & secret in Meteor settings.");
    return;
  }
  // Don't force the user to specify a region, it is usually fine.
  if (! Meteor.settings.aws.region) {
    console.log("Defaulting to the region: us-east-1");
  }
  AWS.config.update({
    accessKeyId: Meteor.settings.aws.key,
    secretAccessKey: Meteor.settings.aws.secret,
    region: "us-east-1" || Meteor.settings.aws.region
  });
  AWSInterface.lambda = new AWS.Lambda();
});


// Load mixins of a specific type from the settings into a provided
// collection. If no mixins are provided, remove all elements from the
// collection.
loadMixins = function (Mixins, mixinType) {
  var mixinData = Meteor.settings[mixinType];

  // If no mixins are specified for the neural net, remove any existing entries.
  if (! mixinData) {
    var msg = "Settings did not specify any mixin data for " + mixinType + ".";
    if (Mixins.findOne()){
        msg += "Removing mixin data for  " + mixinType + ".";
        Mixins.remove({});
    }
    console.log(msg);
    return;
  }

  // Remove any left-over mixins.
  _.each(Mixins.find().fetch(), function (existingMixin) {
//    if (! mixinData[existingMixin._id]) {
      Mixins.remove({ _id: existingMixin._id });
//    }
  });

   // Load in the new data.
  _.each(mixinData, function (value, id) {
     Mixins.upsert({_id: id}, _.extend({letter: id}, value));
  });
};
