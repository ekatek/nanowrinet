// Intialize the Markov mixins from the provided configuration file.
var Mixins = new Mongo.Collection('markov-mixins');
Meteor.startup(function () {
  loadMixins(Mixins, "markov-mixins");
});
Meteor.publish("markov-mixins", function () {
  return Mixins.find({});
});

Meteor.methods({
  calculateMarkovChain: function (req) {
   check(req, {
       mixin: String,
       text: [String]
    });
    // If the work is too long, cut it off and give the user some text anyway.
    if (req.text.length > 50000) {
      req.text = _.first(req.text, 45000);
    }
    var length = 50000 - req.text.length;

    var mixin = Mixins.findOne({ letter: req.mixin });
    if (! mixin) {
      console.log("Unknown mixins.");
      return "something went wrong: unknown author mixin";
    }

    // Call out to AWS Lambda
    var lambdaParams = {
      FunctionName: "markov-chainer",
      InvocationType: 'RequestResponse',
      LogType: 'None',
      Payload: JSON.stringify({
        userText: req.text.join(' '),
        mixin: mixin["filename"],
        length: length
      })
    };
    console.log("invoking markov-chainer");

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
