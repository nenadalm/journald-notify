[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)

# journald-notify
systemd's journal is awesome. Wouldn't it be more awesome if it could send notifications?

journald-notify is a daemon that listens to systemd's journal and sends notifications based on filters that you specify. Currently it supports sending push notifications through SMTP or [Pushbullet](https://www.pushbullet.com/), and also notifications to the notification daemon, by way of notify-send.

## Versioning

Version contains 3 numbers: `x.y.z`

- `x` - incremented when there are breaking changes for users of the app (e.g. change of configuration format)
- `y` - incremented when there are new features
- `z` - incremented when there are only bugfixes

When `x` changes, `y` and `z` should be 0.
When `y` changes, `z` should be 0.

## Usage
See `examples/journald-notify.json` for an example of a configuration file. There are two subcommands to aid you in testing your configuration:

1. `journald-notify -c /path/to/config.json test_notifiers` will try to send a test message through all of your notifiers.
2. `journald-notify -c /path/to/config.json test_filters` will run through your journal history and print entries matching your filters.

Once your configuration is set you can run `journald-notify -c /path/to/config.json run` and wait for push notifications.

You can also check out `examples/journald-notify.service` for an example systemd unit file.

### Version 2
In addition to all of the new features you can make use of in v2, such as filtering notifications based on captured values from the matching regexes, there are two crucial differences between v1 config and v2 config:

- All notifiers must now have a unique identifier. These are referenced when specifying which messages should be sent to which notifiers.
- All capturing groups in matching regexes must now be named. Non-named capturing groups will not be available for display and filtering purposes.

## Notifier configuration

All notifiers support an optional `retry_interval` setting. This should be a positive integer that indicates how long the notifier should wait after it encounters an error before trying again.

### Pushbullet

#### `key` (required)
Your Pushbullet API key.

#### `prepend_hostname` (optional, default=`true`)
Whether or not the hostname of the machine should be prepended to the title of notifications.

### SMTP

#### `host` (required)
The hostname of the SMTP server you intend to use.

#### `from_addr` (required)
The email address from which emails should be sent.

#### `to_addrs` (required)
A list of email addresses to which notification emails should be sent.

#### `port` (optional)
Port number to use for SMTP. Defaults to the appropriate port based on whether or not TLS is being used.

#### `tls` (optional, default=`true`)
Whether or not TLS should be used when connecting to the SMTP server.

#### `username` (optional)
The username required to connect to the SMTP server.

#### `password` (optional)
The password required to connect to the SMTP server.

### notify-send

Due to the nature of how the notification daemon works in most Linux distributions, you generally need to use [`notify-send-headless`](https://proc.readthedocs.io/en/latest/api.html#module-proc.notify) with `sudo` when attempting to display notifications from a daemon process. As such, this is the default configuration for the `notify-send` notifier.

#### `sudo` (optional, default=`true`)
If this is set to `true`, you will need to ensure that the user running `journald-notify` has permission to run `notify-send` or `notify-send-headless` with passwordless sudo. Note that you don't need to whitelist both - if you're using `notify-send-headless`, you don't need to whitelist `notify-send`.

#### `headless` (optional, default=`true`)
Whether or not `notify-send-headless` should be used instead of `notify-send`.

## Notes
This is a fork of [`pushjournal`](https://github.com/r-darwish/pushjournal) by r-darwish. I re-wrote most of the code because I was unhappy about a few things. Most notably, it would not start reading from the journal until it had sent the boot notification, and it would not reliably detect the public and private IP addresses unless network connectivity was available as soon as the program was launched. This rewrite solves those problems, and also stops it from spamming into the journal itself during periods where internet connectivity is lacking.

Other motivations for the rewrite include removing the unnecessary dependencies on the logbook and yaml packages. JSON configuration is just as good and comes built-in with python, while YAML support does not. Also, python's built-in logging module is more than good enough for the majority of problems.

Finally, this rewrite is more flexible with the filters it lets you apply. You can specify one or more services that a filter should target specifically, you can ignore notifications based on what values are captured from the matching regex, or you can specify none at all and just use it for boot notifications.
