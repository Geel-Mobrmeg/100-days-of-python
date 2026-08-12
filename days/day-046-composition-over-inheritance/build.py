"""Day 046 build — a four-level chain, rebuilt from components.

    python3 build.py

THE STARTING POINT — a hierarchy of the kind that appears in every codebase
that has been alive for two years:

    Notifier
      └── LoggedNotifier            adds logging
            └── RetryingNotifier    adds retries
                  └── EmailRetryingNotifier   ...and is finally an email

Each level added one capability by subclassing the one before. It works. It
is also the shape that cannot answer "I want retries but not logging", and
where nobody can tell you what send() actually does without opening four
classes.

BOTH VERSIONS RUN BELOW, produce the same output for the case they share,
and are then asked for something only one of them can do.
"""

import time

WIDTH = 78


# ###########################################################################
# VERSION 1 — THE CHAIN
# ###########################################################################

class Notifier:
    """Level 1: knows how to send."""

    def __init__(self, recipient):
        self.recipient = recipient
        self.sent = []

    def send(self, message):
        self.sent.append(message)
        return f"delivered to {self.recipient}"


class LoggedNotifier(Notifier):
    """Level 2: adds logging."""

    def __init__(self, recipient, log):
        super().__init__(recipient)
        self.log = log

    def send(self, message):
        self.log.append(f"sending {message!r}")
        result = super().send(message)
        self.log.append(f"result: {result}")
        return result


class RetryingNotifier(LoggedNotifier):
    """Level 3: adds retries. Cannot exist without the logging above it."""

    def __init__(self, recipient, log, attempts=3, fail_times=0):
        super().__init__(recipient, log)
        self.attempts = attempts
        self.fail_times = fail_times
        self._failures = 0

    def send(self, message):
        for attempt in range(1, self.attempts + 1):
            try:
                if self._failures < self.fail_times:
                    self._failures += 1
                    raise ConnectionError("transient failure")
                return super().send(message)
            except ConnectionError as exc:
                self.log.append(f"attempt {attempt} failed: {exc}")
        raise RuntimeError(f"gave up after {self.attempts} attempts")


class EmailRetryingNotifier(RetryingNotifier):
    """Level 4: and finally, it is email."""

    def send(self, message):
        return super().send(f"Subject: Notification\n\n{message}")


# ###########################################################################
# VERSION 2 — THE COMPONENTS
# ###########################################################################

class EmailChannel:
    """Sends. That is all it does."""

    def __init__(self, recipient):
        self.recipient = recipient
        self.sent = []

    def deliver(self, message):
        self.sent.append(message)
        return f"delivered to {self.recipient}"


class SmsChannel:
    def __init__(self, number):
        self.number = number
        self.sent = []

    def deliver(self, message):
        self.sent.append(message[:160])
        return f"sms to {self.number}"


class FlakyChannel:
    """Fails a fixed number of times, then works. For testing retries."""

    def __init__(self, inner, fail_times):
        self.inner = inner
        self.fail_times = fail_times
        self._failures = 0

    def deliver(self, message):
        if self._failures < self.fail_times:
            self._failures += 1
            raise ConnectionError("transient failure")
        return self.inner.deliver(message)


class EmailFormatter:
    def format(self, message):
        return f"Subject: Notification\n\n{message}"


class PlainFormatter:
    def format(self, message):
        return message


class ListLogger:
    def __init__(self):
        self.lines = []

    def log(self, line):
        self.lines.append(line)


class NullLogger:
    """The component that means "do not log". No subclass required."""

    def log(self, line):
        pass


class RetryPolicy:
    def __init__(self, attempts=3, delay=0.0):
        self.attempts = attempts
        self.delay = delay

    def run(self, action, logger):
        for attempt in range(1, self.attempts + 1):
            try:
                return action()
            except ConnectionError as exc:
                logger.log(f"attempt {attempt} failed: {exc}")
                if attempt < self.attempts:
                    time.sleep(self.delay)
        raise RuntimeError(f"gave up after {self.attempts} attempts")


class NoRetry:
    """The component that means "do not retry"."""

    attempts = 1

    def run(self, action, logger):
        return action()


class NotificationService:
    """Holds four collaborators. Inherits from nothing.

    Every capability the four-level chain provided is here as an ARGUMENT,
    which means every combination is reachable — including the ones the
    chain could not express.
    """

    def __init__(self, channel, formatter=None, logger=None, retry=None):
        self.channel = channel
        self.formatter = formatter or PlainFormatter()
        self.logger = logger or NullLogger()
        self.retry = retry or NoRetry()

    def send(self, message):
        body = self.formatter.format(message)
        self.logger.log(f"sending {message!r}")
        result = self.retry.run(lambda: self.channel.deliver(body), self.logger)
        self.logger.log(f"result: {result}")
        return result


# ###########################################################################
# THEY AGREE ON THE CASE THEY SHARE
# ###########################################################################

print("=" * WIDTH)
print(f"{'THE SAME JOB, TWO DESIGNS':^{WIDTH}}")
print("=" * WIDTH)

chain_log = []
chain = EmailRetryingNotifier("ada@example.com", chain_log, attempts=3,
                              fail_times=2)
chain_result = chain.send("your order has shipped")

composed_log = ListLogger()
composed = NotificationService(
    channel=FlakyChannel(EmailChannel("ada@example.com"), fail_times=2),
    formatter=EmailFormatter(),
    logger=composed_log,
    retry=RetryPolicy(attempts=3),
)
composed_result = composed.send("your order has shipped")

print(f"{'chain result':<30}{chain_result:>{WIDTH - 30}}")
print(f"{'composed result':<30}{composed_result:>{WIDTH - 30}}")
print(f"{'same result':<30}"
      f"{str(chain_result == composed_result):>{WIDTH - 30}}")
print(f"{'same message delivered':<30}"
      f"{str(chain.sent == composed.channel.inner.sent):>{WIDTH - 30}}")
print(f"{'same number of log lines':<30}"
      f"{str(len(chain_log) == len(composed_log.lines)):>{WIDTH - 30}}")

print("\n  the log, from the composed version:")
for line in composed_log.lines:
    print(f"    {line}")

# ###########################################################################
# NOW ASK FOR SOMETHING THE CHAIN CANNOT DO
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE REQUESTS THAT BREAK THE CHAIN':^{WIDTH}}")
print("=" * WIDTH)

requests = [
    ("retries, but NO logging",
     NotificationService(
         channel=FlakyChannel(EmailChannel("a@b.c"), 1),
         retry=RetryPolicy(attempts=2))),
    ("logging, but NO retries",
     NotificationService(
         channel=EmailChannel("a@b.c"), logger=ListLogger())),
    ("SMS instead of email",
     NotificationService(channel=SmsChannel("+44 7700 900000"))),
    ("SMS with retries and logging",
     NotificationService(
         channel=FlakyChannel(SmsChannel("+44 7700 900000"), 1),
         logger=ListLogger(), retry=RetryPolicy(attempts=3))),
    ("plain email, nothing else",
     NotificationService(channel=EmailChannel("a@b.c"))),
]

for label, service in requests:
    result = service.send("hello")
    print(f"  {label:<34}{result:>{WIDTH - 36}}")

print("""
  Five configurations, ONE class, no new subclasses.

  For the chain, each of those needs a NEW CLASS — and the first two are
  not even expressible, because RetryingNotifier inherits LoggedNotifier.
  You cannot have retries without logging without rewriting the hierarchy.

  The combinatorics: 2 channels x 2 formatters x 2 loggers x 2 retry
  policies is 16 behaviours. Composed, that is 8 small classes. As a
  hierarchy it is 16 subclasses, or a chain that cannot express half of
  them.""")

# ###########################################################################
# AND THE ONE THAT MATTERS MOST: TESTING
# ###########################################################################

print("=" * WIDTH)
print(f"{'TESTING':^{WIDTH}}")
print("=" * WIDTH)


class SpyChannel:
    """A test double. Twelve lines, no inheritance, no mocking library."""

    def __init__(self):
        self.calls = []

    def deliver(self, message):
        self.calls.append(message)
        return "spy: ok"


spy = SpyChannel()
log = ListLogger()
service = NotificationService(channel=spy, formatter=EmailFormatter(),
                             logger=log)
service.send("under test")

print(f"  {'the channel was called':<44}{len(spy.calls) == 1!s:>{WIDTH - 46}}")
print(f"  {'with the FORMATTED message':<44}"
      f"{spy.calls[0].startswith('Subject:')!s:>{WIDTH - 46}}")
print(f"  {'and the logger recorded both stages':<44}"
      f"{len(log.lines) == 2!s:>{WIDTH - 46}}")
print(f"  {'nothing was actually sent anywhere':<44}"
      f"{'True':>{WIDTH - 46}}")

print("""
  A twelve-line class and a constructor argument. No mocking library, no
  monkeypatching, no network.

  To test the CHAIN you would subclass EmailRetryingNotifier and override
  send() — at which point you are no longer testing the class you ship, you
  are testing a subclass of it. That is the single strongest practical
  argument for composition, and it is why Day 58's monkeypatch exists
  mostly to rescue designs that did not do this.""")

# ###########################################################################
# THE HONEST COMPARISON
# ###########################################################################

print()
print("=" * WIDTH)
print("""WHAT EACH ONE COSTS

  THE CHAIN
    +  short to write the first time; each level is a few lines
    +  one name to instantiate
    -  cannot express retries-without-logging AT ALL
    -  four files to read to understand one send()
    -  changing Notifier.send silently changes all four
    -  testable only by subclassing the thing you ship

  THE COMPONENTS
    +  every combination reachable, including ones not yet imagined
    +  each piece is ~10 lines and independently testable
    +  a test double is a class with one method
    +  a new channel touches nothing that exists
    -  more classes, and more to name
    -  the call site is longer — four arguments instead of one
    -  needs an agreed shape (deliver/format/log/run) or nothing can be
       swapped. Day 49's Protocol is how you write that down.

THE HONEST SUMMARY: composition costs more up front and less every time
afterwards. Which is exactly the trade you want on anything that lives
longer than a fortnight — and exactly the wrong trade for a script.""")
print("=" * WIDTH)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Add a SlackChannel. Composed: one class, ten lines, nothing else
#     changes. Then add it to the chain and count what you had to touch.
#
#   * Add "log to a file as well as a list". Composed: a MultiLogger
#     holding two loggers — which is itself composition, one level down.
#     In the chain it is a fifth level, or a flag on the second.
#
#   * The components have no declared interface: NotificationService just
#     hopes every channel has .deliver(). Write it down with typing.Protocol
#     (Day 49) and let mypy check it.
#
#   * FlakyChannel WRAPS another channel rather than replacing it — that is
#     the Decorator pattern (Day 96), and it composes with anything.
#     Try writing a RateLimitedChannel the same way.
#
#   * Find one class in your own code that inherits to reuse. Rewrite it.
