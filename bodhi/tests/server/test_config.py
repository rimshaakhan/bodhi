# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import unittest

import mock

from bodhi.server import config


class BodhiConfigGetItemTests(unittest.TestCase):
    """Tests for the ``__getitem__`` method on the :class:`BodhiConfig` class."""

    def setUp(self):
        self.config = config.BodhiConfig()
        self.config.load_config = mock.Mock()
        self.config['password'] = 'hunter2'

    def test_not_loaded(self):
        """Assert calling ``__getitem__`` causes the config to load."""
        self.assertFalse(self.config.loaded)
        self.assertEqual('hunter2', self.config['password'])
        self.config.load_config.assert_called_once()

    def test_loaded(self):
        """Assert calling ``__getitem__`` when the config is loaded doesn't reload the config."""
        self.config.loaded = True

        self.assertEqual('hunter2', self.config['password'])
        self.assertEqual(0, self.config.load_config.call_count)

    def test_missing(self):
        """Assert you still get normal dictionary errors from the config."""
        self.assertRaises(KeyError, self.config.__getitem__, 'somemissingkey')


class BodhiConfigGetTests(unittest.TestCase):
    """Tests for the ``get`` method on the :class:`BodhiConfig` class."""

    def setUp(self):
        self.config = config.BodhiConfig()
        self.config.load_config = mock.Mock()
        self.config['password'] = 'hunter2'

    def test_not_loaded(self):
        """Assert calling ``get`` causes the config to load."""
        self.assertFalse(self.config.loaded)
        self.assertEqual('hunter2', self.config.get('password'))
        self.config.load_config.assert_called_once()

    def test_loaded(self):
        """Assert calling ``get`` when the config is loaded doesn't reload the config."""
        self.config.loaded = True

        self.assertEqual('hunter2', self.config.get('password'))
        self.assertEqual(0, self.config.load_config.call_count)

    def test_missing(self):
        """Assert you get ``None`` when the key is missing."""
        self.assertEqual(None, self.config.get('somemissingkey'))


class BodhiConfigPopItemTests(unittest.TestCase):
    """Tests for the ``pop`` method on the :class:`BodhiConfig` class."""

    def setUp(self):
        self.config = config.BodhiConfig()
        self.config.load_config = mock.Mock()
        self.config['password'] = 'hunter2'

    def test_not_loaded(self):
        """Assert calling ``pop`` causes the config to load."""
        self.assertFalse(self.config.loaded)
        self.assertEqual('hunter2', self.config.pop('password'))
        self.config.load_config.assert_called_once()

    def test_loaded(self):
        """Assert calling ``pop`` when the config is loaded doesn't reload the config."""
        self.config.loaded = True

        self.assertEqual('hunter2', self.config.pop('password'))
        self.assertEqual(0, self.config.load_config.call_count)

    def test_removes(self):
        """Assert the configuration is removed with ``pop``."""
        self.assertEqual('hunter2', self.config.pop('password'))
        self.assertRaises(KeyError, self.config.pop, 'password')

    def test_get_missing(self):
        """Assert you still get normal dictionary errors from the config."""
        self.assertRaises(KeyError, self.config.pop, 'somemissingkey')


class BodhiConfigCopyTests(unittest.TestCase):
    """Tests for the ``copy`` method on the :class:`BodhiConfig` class."""

    def setUp(self):
        self.config = config.BodhiConfig()
        self.config.load_config = mock.Mock()
        self.config['password'] = 'hunter2'

    def test_not_loaded(self):
        """Assert calling ``copy`` causes the config to load."""
        self.assertFalse(self.config.loaded)
        self.assertEqual({'password': 'hunter2'}, self.config.copy())
        self.config.load_config.assert_called_once()

    def test_loaded(self):
        """Assert calling ``copy`` when the config is loaded doesn't reload the config."""
        self.config.loaded = True

        self.assertEqual({'password': 'hunter2'}, self.config.copy())
        self.assertEqual(0, self.config.load_config.call_count)


class BodhiConfigLoadConfig(unittest.TestCase):

    @mock.patch('bodhi.server.config.get_appsettings')
    def test_loads_defaults(self, get_appsettings):
        """Test that defaults are loaded."""
        c = config.BodhiConfig()

        c.load_config({'session.secret': 'secret', 'authtkt.secret': 'secret'})

        self.assertEqual(c['top_testers_timeframe'], 7)

    @mock.patch('bodhi.server.config.get_configfile', mock.Mock(return_value='/some/config.ini'))
    @mock.patch('bodhi.server.config.get_appsettings')
    def test_marks_loaded(self, mock_appsettings):
        c = config.BodhiConfig()
        mock_appsettings.return_value = {'password': 'hunter2', 'session.secret': 'ssshhhhh',
                                         'authtkt.secret': 'keepitsafe'}

        c.load_config()

        mock_appsettings.assert_called_once_with('/some/config.ini')
        self.assertTrue(('password', 'hunter2') in c.items())
        self.assertTrue(c.loaded)

    @mock.patch('bodhi.server.config.get_appsettings')
    def test_validates(self, get_appsettings):
        """Test that the config is validated."""
        c = config.BodhiConfig()

        with self.assertRaises(ValueError) as exc:
            c.load_config({'fedmsg_enabled': 'not a bool', 'session.secret': 'secret',
                           'authtkt.secret': 'secret'})

        self.assertEqual(
            str(exc.exception),
            ('Invalid config values were set: \n\tfedmsg_enabled: "not a bool" cannot be '
             'interpreted as a boolean value.'))

    @mock.patch('bodhi.server.config.get_appsettings')
    def test_with_settings(self, get_appsettings):
        """Test with the optional settings parameter."""
        c = config.BodhiConfig()

        c.load_config({'wiki_url': 'test', 'session.secret': 'secret', 'authtkt.secret': 'secret'})

        self.assertEqual(c['wiki_url'], 'test')
        self.assertEqual(get_appsettings.call_count, 0)


class BodhiConfigLoadDefaultsTests(unittest.TestCase):
    """Test the BodhiConfig._load_defaults() method."""
    @mock.patch.dict('bodhi.server.config.BodhiConfig._defaults', {'one': {'value': 'default'}},
                     clear=True)
    def test_load_defaults(self):
        c = config.BodhiConfig()

        c._load_defaults()

        self.assertEqual(c, {'one': 'default'})


class BodhiConfigValidate(unittest.TestCase):
    def test_comps_unsafe_http_url(self):
        """Ensure that setting comps_url to http://example.com fails validation."""
        c = config.BodhiConfig()
        c.load_config()
        c['comps_url'] = 'http://example.com'

        with self.assertRaises(ValueError) as exc:
            c._validate()

        self.assertEqual(str(exc.exception), ('Invalid config values were set: \n\tcomps_url: This '
                                              'setting must be a URL starting with https://.'))

    def test_valid_config(self):
        """A valid config should not raise Exceptions."""
        c = config.BodhiConfig()
        c.load_config({'session.secret': 'secret', 'authtkt.secret': 'secret'})

        # This should not raise an Excepton
        c._validate()


class GenerateListValidatorTests(unittest.TestCase):
    """Tests the _generate_list_validator() function."""
    def test_custom_splitter(self):
        """Test with a non-default splitter."""
        result = config._generate_list_validator('|')('thing 1| thing 2')

        self.assertEqual(result, [u'thing 1', u'thing 2'])
        self.assertTrue(all([isinstance(v, unicode) for v in result]))

    def test_custom_validator(self):
        """Test with a non-default validator."""
        result = config._generate_list_validator(validator=int)('1 23 456')

        self.assertEqual(result, [1, 23, 456])
        self.assertTrue(all([isinstance(v, int) for v in result]))

    def test_with_defaults(self):
        """Test with the default parameters."""
        result = config._generate_list_validator()('play it again sam')

        self.assertEqual(result, [u'play', u'it', u'again', u'sam'])
        self.assertTrue(all([isinstance(v, unicode) for v in result]))

    def test_with_list(self):
        """Test with a list."""
        result = config._generate_list_validator(validator=int)(['1', '23', 456])

        self.assertEqual(result, [1, 23, 456])
        self.assertTrue(all([isinstance(v, int) for v in result]))

    def test_wrong_type(self):
        """Test with a non string, non list data type."""
        with self.assertRaises(ValueError) as exc:
            config._generate_list_validator()({'lol': 'wut'})

        self.assertEqual(str(exc.exception), '"{\'lol\': \'wut\'}" cannot be intepreted as a list.')


class ValidateBoolTests(unittest.TestCase):
    """This class contains tests for the _validate_bool() function."""
    def test_bool(self):
        """Test with boolean values."""
        self.assertTrue(config._validate_bool(False) is False)
        self.assertTrue(config._validate_bool(True) is True)

    def test_other(self):
        """Test with a non-string and non-bool type."""
        with self.assertRaises(ValueError) as exc:
            config._validate_bool({'not a': 'bool'})

        self.assertEqual(str(exc.exception), "\"{'not a': 'bool'}\" is not a bool or a string.")

    def test_string_falsey(self):
        """Test with "falsey" strings."""
        for s in ('f', 'false', 'n', 'no', 'off', '0'):
            self.assertTrue(config._validate_bool(s) is False)

    def test_string_other(self):
        """Test with an ambiguous string."""
        with self.assertRaises(ValueError) as exc:
            config._validate_bool('oops typo')

        self.assertEqual(str(exc.exception),
                         '"oops typo" cannot be interpreted as a boolean value.')

    def test_string_truthy(self):
        """Test with "truthy" strings."""
        for s in ('t', 'true', 'y', 'yes', 'on', '1'):
            self.assertTrue(config._validate_bool(s) is True)


class ValidateColorTests(unittest.TestCase):
    """Test the _validate_color() function."""
    def test_non_string(self):
        """A non-string parameter should raise a ValueError."""
        with self.assertRaises(ValueError) as exc:
            config._validate_color(['this', 'should', 'not', 'work'])

        self.assertEqual(str(exc.exception),
                         "\"['this', 'should', 'not', 'work']\" is not a valid color expression.")

    def test_valid_color(self):
        """A valid color string should not raise a ValueError and should be converted to unicode."""
        color = config._validate_color('#65FE00')

        self.assertEqual(color, u'#65FE00')
        self.assertTrue(isinstance(color, unicode))

    def test_wrong_base(self):
        """A string that isn't a base-16 number should raise a ValueError."""
        with self.assertRaises(ValueError) as exc:
            config._validate_color('#65FE0G')

        self.assertEqual(str(exc.exception), '"#65FE0G" is not a valid color expression.')

    def test_wrong_first_char(self):
        """A string that doesn't start with # should raise a ValueError."""
        with self.assertRaises(ValueError) as exc:
            config._validate_color('065FE00')

        self.assertEqual(str(exc.exception), '"065FE00" is not a valid color expression.')

    def test_wrong_length(self):
        """A string with the wrong length should raise a ValueError."""
        with self.assertRaises(ValueError) as exc:
            config._validate_color('#65FE0')

        self.assertEqual(str(exc.exception), '"#65FE0" is not a valid color expression.')


class ValidateFernetKey(unittest.TestCase):
    """This class contains tests for the _validate_fernet_key() function."""
    def test_changeme(self):
        """A value of CHANGE should raise a ValueError."""
        with self.assertRaises(ValueError) as exc:
            config._validate_fernet_key('CHANGEME')

        self.assertEqual(str(exc.exception), 'This setting must be changed from its default value.')

    def test_non_base64_key(self):
        """A non-base64 key should also raise a ValueError."""
        with self.assertRaises(ValueError) as exc:
            config._validate_fernet_key('not base 64')

        self.assertEqual(str(exc.exception), 'Fernet key must be 32 url-safe base64-encoded bytes.')

    def test_valid_key(self):
        """A valid key should be converted to a unicode object."""
        key = 'gFqE6rcBXVLssjLjffsQsAa-nlm5Bg06MTKrVT9hsMA='
        result = config._validate_fernet_key(key)

        self.assertEqual(result, key)
        self.assertTrue(type(result), str)

    def test_wrong_length_key(self):
        """An key with wrong length should raise a ValueError."""
        with self.assertRaises(ValueError) as exc:
            config._validate_fernet_key('VGhpcyBpcyBhIHRlc3Qgb2YgdGhlIHN5c3RlbS4K')

        self.assertEqual(str(exc.exception), 'Fernet key must be 32 url-safe base64-encoded bytes.')


class ValidateNoneOrTests(unittest.TestCase):
    """Test the _validate_none_or() function."""
    def test_with_none(self):
        """Assert that None is allowed."""
        result = config._validate_none_or(unicode)(None)

        self.assertTrue(result is None)

    def test_with_string(self):
        """Assert that a string is validated and converted to unicode."""
        result = config._validate_none_or(unicode)('unicode?')

        self.assertEqual(result, u'unicode?')
        self.assertTrue(isinstance(result, unicode))


class ValidatePathTests(unittest.TestCase):
    """Test the _validate_path() function."""
    def test_path_does_not_exist(self):
        """Test with a path that does not exist."""
        with self.assertRaises(ValueError) as exc:
            config._validate_path('/does/not/exist')

        self.assertEqual(str(exc.exception), '"/does/not/exist" does not exist.')

    def test_path_exists(self):
        """Test with a path that exists."""
        result = config._validate_path(__file__)

        self.assertEqual(result, __file__)
        self.assertTrue(isinstance(result, unicode))


class ValidateSecretTests(unittest.TestCase):
    """Test the _validate_secret() function."""
    def test_with_changeme(self):
        """Ensure that CHANGEME raises a ValueError."""
        with self.assertRaises(ValueError) as exc:
            config._validate_secret('CHANGEME')

        self.assertEqual(str(exc.exception), 'This setting must be changed from its default value.')

    def test_with_secret(self):
        """Ensure that a secret gets changed to a unicode."""
        result = config._validate_secret('secret')

        self.assertEqual(result, u'secret')
        self.assertTrue(isinstance(result, unicode))


class ValidateTLSURL(unittest.TestCase):
    """Test the _validate_tls_url() function."""
    def test_with_http(self):
        """Ensure that http:// URLs raise a ValueError."""
        with self.assertRaises(ValueError) as exc:
            config._validate_tls_url('http://example.com')

        self.assertEqual(str(exc.exception), 'This setting must be a URL starting with https://.')

    def test_with_https(self):
        """Ensure that https:// urls get converted to unicode."""
        result = config._validate_tls_url('https://example.com')

        self.assertEqual(result, u'https://example.com')
        self.assertTrue(isinstance(result, unicode))
