# Author: Michael DiBernardo (mikedebo@gmail.com)
from django import forms
from django.forms import ValidationError

import datetime
import re

class KungfuTimeField(forms.Field):
    """
    Extension to Django's time fields that parses a much larger range of times
    without explicitly needing to specify all the time formats yourself.
    """

    # Matches any string with a 24-hourish format (sans AM/PM) but puts no
    # limits on the size of the numbers (e.g. 64:99 is OK.)
    _24_HOUR_PATTERN_STRING = r'^\s*(?P<hour>\d\d?)\s*:?\s*(?P<minute>\d\d)?\s*(:?\s*(?P<second>\d\d)\s*)?'

    # Matches any string with a 12-hourish format (with AM/PM) but puts no
    # limits on the size of the numbers (e.g. 64:99pm is OK.)
    _TIME_PATTERN_STRING = _24_HOUR_PATTERN_STRING + \
        r'((?P<ampm>[AaPp])\s*\.?\s*[Mm]?\s*\.?\s*)?$'

    # Matcher for our time pattern.
    _TIME_PATTERN = re.compile(_TIME_PATTERN_STRING)

    # Validation error messages.
    _ERROR_MESSAGES = {
        'invalid' : u'Enter a valid time.',
    }

    def __init__(self, *args, **kwargs):
        """
        Create a new KungFuTimeField with the mojo of a thousand TimeFields.
        """
        super(KungfuTimeField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        Parses datetime from the given value. If it can't figure it out, throws
        a ValidationError.
        """
        super(KungfuTimeField, self).clean(value)
        if not value:
            return None
        if isinstance(value, datetime.time):
            return value
        cleaned = self._parse_time(value)
        return cleaned

    def _parse_time(self, value):
        """
        Tries to recognize a time using our hefty regexp. If it doesn't match
        the regexp, throws a validation error. If it DOES match but the
        resulting numbers are out of range (e.g. an hour of 99), will also
        throw a ValidationError.
        """
        match = self._TIME_PATTERN.match(value)
        if not match:
            raise ValidationError(self._ERROR_MESSAGES['invalid'])

        # Hour has to be there because it's required in the regexp. Set the
        # minute to 0 for now. We dunno if there's AM/PM or not.
        (hour, minute, second, ampm) = (int(match.group('hour')), 
                                        0, 0, match.group('ampm'))

        # Let's see if the user typed a minute ...
        try:
            # Raises TypeError if group fetch returns None.
            minute = int(match.group('minute'))
        except TypeError:
            pass  

        # ... or a second.
        try:
            # Raises TypeError if group fetch returns None.
            second = int(match.group('second'))
        except TypeError:
            pass  

        if ampm:
            hour = self._handle_twelve_hour_time(hour, minute, second, ampm)

        # If the numbers are out of range, we'll find out here.
        try:
            return datetime.time(hour, minute, second)
        except ValueError:
            raise ValidationError(self._ERROR_MESSAGES['invalid'])

        # I don't expect any other problems, but if there are, they'll
        # propagate.

    def _handle_twelve_hour_time(self, hour, minute, second, ampm):
        """
        Detect 24 hour time with an am/pm (e.g. 18:30:00pm, 0:30:00am)
        and do the necessary transform for converting pm times to 24
        hour times.
        """
        if hour < 1 or hour > 12:
            raise ValidationError(self._ERROR_MESSAGES['invalid'])
        elif ampm.lower() == "a" and hour == 12:
            return 0
        elif ampm.lower() == "p" and 1 <= hour and hour <= 11:
            return hour + 12
        else:
            return hour

"""
Tests that our extension to the Django time field can parse a wide variety of
time formats.
"""

# Author: Michael DiBernardo (mikedebo@gmail.com)
from kungfutime import KungfuTimeField
from django.forms import ValidationError

import datetime as dt
import unittest

class TestTimeParsing(unittest.TestCase):

    def setUp(self):
        self.field = KungfuTimeField()

    def test24HourFormats(self):
        """
        Tests a variety of 24 hour formats.
        """
        twofour_hour_tests = (
            ("8:30", dt.time(8, 30)),
            ("14:30", dt.time(14, 30)),
            ("8", dt.time(8)),
            ("16", dt.time(16)),
            ("1742", dt.time(17, 42)),
            ("856", dt.time(8, 56)),
            ("101", dt.time(1, 01)),
            ("1 01", dt.time(1, 01)),
            ("13 01", dt.time(13, 01)),
            ("01 01", dt.time(1, 1)),
            (" 13     01 ", dt.time(13, 01)),
        )

        for (input, expected) in twofour_hour_tests:
            self.assertTimeEquals(input, expected)

    def test12HourFormats(self):
        """
        Tests a variety of 12 hour formats.
        """
        twelve_hour_tests = (
            ("12:30pm", dt.time(12, 30)),
            ("12:30PM", dt.time(12, 30)),
            ("12:30P.m.", dt.time(12, 30)),
            ("12:30 pm  ", dt.time(12, 30)),
            ("12:30 P m", dt.time(12, 30)),
            ("12:30 p .  M  .", dt.time(12, 30)),
            ("12:30p", dt.time(12, 30)),
            ("12:30  p", dt.time(12, 30)),
            ("12 30pm", dt.time(12, 30)),
            ("12  30 pm", dt.time(12, 30)),
            ("1230 p m", dt.time(12, 30)),
            ("  1230 p m", dt.time(12, 30)),
            ("12  30 p .  m  .", dt.time(12, 30)),
            ("1:30am", dt.time(1, 30)),
            ("1:30 am  ", dt.time(1, 30)),
            ("1:30 a m", dt.time(1, 30)),
            ("1:30 a .  m  .", dt.time(1, 30)),
            ("1:30a", dt.time(1, 30)),
            ("1:30  a", dt.time(1, 30)),
            ("1 30am", dt.time(1, 30)),
            ("  1  30 am", dt.time(1, 30)),
            ("130 a m", dt.time(1, 30)),
            ("3:30 p m", dt.time(15, 30)),
            ("     1  30 a .  m  ", dt.time(1, 30)),
        )

        for (input, expected) in twelve_hour_tests:
            self.assertTimeEquals(input, expected)

    def testBadTimes(self):
        """
        Tests a variety of times that should bork and die, not necessarily in
        that order.
        """
        bad_inputs = (
            "",
            " aa ",
            "12345",
            "1340am",
            "030pm",
            "25:23",
            "24:10",
            "this ain't nothing like a time",
            "-2:30",
        )

        for bad_input in bad_inputs:
            try:
                self.field.clean(bad_input)
                self.fail("Bad input %s validated." % bad_input)
            except AssertionError, e:
                raise e
            except ValidationError, e:
                pass
            except Exception, e:
                self.fail("Validator threw unexpected exception %s" % str(e))

    def assertTimeEquals(self, timestring, expected):
        """
        Try to parse a time, and if it throws an exception, fail.
        """
        try:
            actual = self.field.clean(timestring)
            self.assertEquals(actual, expected,
                    "String %s did not parse to expected datetime %s: Got %s" %
                    (timestring, str(expected), str(actual))
            )
        except AssertionError, e:
            # Propagate assertion failures.
            raise e
        except ValidationError, e:
            self.fail("String %s did not validate." % timestring)
        except Exception, e:
            self.fail("String %s caused unexpected exception: %s" %
                    (timestring, str(e)))


