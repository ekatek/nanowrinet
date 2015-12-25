// Are we running a markov chain or neural net? Select backend algorithm. We
// could also configure the auxillaries, but there is no point.
var Mixins;
var method;
var label;
var details;
if (Meteor.settings.public.mode === "net") {
  Meteor.subscribe("net-mixins");
  Mixins = new Mongo.Collection("net-mixins");
  method = "calculateNeuralNet";
  label = "NaNoWri Neutral-Net";
  details = "<p> This \"helpful\" webapp will use an " +
     "<a href='https://en.wikipedia.org/wiki/Artificial_neural_network'> artificial neural network </a> " +
     "to generate some more content, in the style of the original. The network has been trained with some " +
     "provided data (for example, several works by James Joyce). The app will amend its values slightly " +
     "based on your input, do some post-processing, and return the result. </p> " +
     "<p> You can also see the Markov-chain version  <a href='http://nanowrikov.meteor.com'>here</a>. </p>";
} else if (Meteor.settings.public.mode === "markov") {
  Meteor.subscribe("markov-mixins");
  Mixins = new Mongo.Collection("markov-mixins");
  method = "calculateMarkovChain";
  label = "NaNoWriMo Autocompleter";
  details = "<p> This \"helpful\" webapp will smash together submitted content and pre-processed sample, " +
     "then use a Markov chainer to generate some text. " +
     "You can also see the Neural Net version  <a href='http://nanowrinet.meteor.com'>here</a>. </p>";
} else {
  console.log("unknown mode");
}
Algorithm = {
  label: label,
  method: method,
  Mixins: Mixins,
  details: details
};
