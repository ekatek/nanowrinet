// Intialize the Neural Net mixins from the provided configuration file.
var Mixins = new Mongo.Collection('net-mixins');
Meteor.startup(function () {
  loadMixins(Mixins, "net-mixins");
});

Meteor.publish("net-mixins", function () {
  return Mixins.find({});
});


Meteor.methods({
  calculateNeuralNet: function (req) {
    check(req, {
       mixin: String,
       text: [String]
    });
    // Find the right mixin
    var mixin = Mixins.findOne({letter: req.mixin});
    if (! mixin) {
      console.log("Unknown mixin:", req.mixin);
      return "something went wrong: unknown author mixin";
    }

    // Call out to AWS Lambda
    var lambdaParams = {
      FunctionName: mixin["lambda-name"],
      InvocationType: 'RequestResponse',
      LogType: 'None',
      Payload: JSON.stringify({
        userText: req.text,
        author: mixin["author-token"],
        length: 1000
      })
    };
    console.log("invoking lambda:", mixin["lambda-name"]);

    // Handle errors and format the text.
    try {
      var result = AWSInterface.lambda.invokeSync(lambdaParams);
    } catch (e) {
      throw new Meteor.Error(JSON.stringify(e));
    }

    if (typeof result.Payload != "string") {
      throw new Meteor.Error(result.Payload);
    }
    return formatText(result.Payload);
  }
});
