// Format the text that we get back from the backend to be more user-friendly
// and text-like. Clean up extra spacing and newlines, etc.
//
// Some of this lives here because it is basically the same for both lambdas,
// and because doing this work on the client is actually faster. :/
formatText = function(text) {

    // Use a regex to hit all occurrences of a string.
    var all = function(s) { return new RegExp(s, 'g'); };

    // Keep double new lines. Remove all other line breaks.
    var token = "NLS";
    text = text.replace(all("\\\\n"), token);
    text = text.replace(all(token + " *" + token), "<br><br>");
    text = text.replace(all(token), " ");

    // Punctuation has extra spaces in front of it. Erase those.
    _.each("!.?", function (p) {
      text = text.replace(all(" \\" + p), p);
    });
    text = text.replace(all("\\\""), '"');

    // Capitalize some special cases. That's just a pet-peeve of mine.
    text = text.replace(all(" i "), " I ");
    text = text.replace(all(" o "), " O! ");

    // Cleanse off extra spaces.
    return text.replace(all("  +"), " ");
};
