Add a "is_truthy" utility to test for true-ish and false-ish string values.

The following values are interpreted as an affirmative value and will return a
boolean True:

True, 1 and these strings in any casing: "y", "yes", "t", "true", "active",
"enabled", "on".

Everything else will be interpreted as False.
