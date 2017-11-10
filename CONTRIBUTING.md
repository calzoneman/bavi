Contributing
============

This project is still in its early stages of implementation.  Contributions are
welcome -- both code and documentation.

Since the project is a work-in-progress right now, please be sure to check for
open Issues and Projects to make sure no one else is already working on the same
thing you intend to do.  If there is not an issue tracking your bug/feature yet,
please create one.

## Code Formatting

Please keep lines to 80 columns or less, as per PEP-8, and indent with 4 spaces.
Name classes with `CamelCase` and functions/variables with `snake_case`.

## Testing

Please include a few unit tests with code changes.  You can run the tests with
the included script `bin/run-unit-tests`.  Tests are implemented using the
Python built-in `unittest` module.

**Note:** `bin/run-unit-tests` assumes you have a virtualenv located at `.env`.
If this is not the case, you can run the tests with:

```sh
/path/to/python -m unittest discover -s test
```

### Manual Testing

It's also preferable to run the bot with your changes and verify it works as
expected.  Some IRC networks will Z-line for disconnecting/reconnecting too
often, so for convenience and to avoid triggering these kinds of limits, you can
run your own IRC server.

I'm running the
[inspircd/inspircd-docker](https://hub.docker.com/r/inspircd/inspircd-docker/)
docker image locally for testing purposes.
