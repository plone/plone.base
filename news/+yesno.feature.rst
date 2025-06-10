Add a "yesno" utility function to test for true-ish and false-ish string values.

The following values are interpreted as if a positive answer was meant and will
return a boolean True:

True, 1 and these strings in any casing: "y", "yes", "t", "true", "on".

Everything else is considered False.
