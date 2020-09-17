from string import Formatter
import os
import sys
import unittest

import crab


# ------------------------------------------------------------------------------
class _MayaSetup(unittest.TestCase):
    """
    Unittest class for unittests in maya.exe or mayapy.exe.
    """

    def __init__(self, *args, **kwargs):
        super(_MayaSetup, self).__init__(*args, **kwargs)
        self._standalone_initialized = False

    def setup(self):
        if not self._standalone_initialized:
            executable_dir, executable = os.path.split(sys.executable)
            if executable == 'maya.exe':
                pass

            elif executable == 'mayapy.exe':
                import maya.standalone
                maya.standalone.initialize()

            self._standalone_initialized = True

    def teardown(self):
        if self._standalone_initialized:
            import maya.cmds

            if float(maya.cmds.about(v=True)) >= 2016.0:
                import maya.standalone
                maya.standalone.uninitialize()

            self._standalone_initialized = False


# ------------------------------------------------------------------------------
class TestConfig(_MayaSetup):

    _available_name_pattern_fields = set(
        data[1]
        for data in Formatter().parse(crab.config.NAME_PATTERN)
        if data[1]
    )

    def test_colours(self):
        colours = [
            crab.config.LEFT_COLOR,
            crab.config.RIGHT_COLOR,
            crab.config.MIDDLE_COLOR,
            crab.config.NON_ANIMATABLE_COLOUR,
            crab.config.GUIDE_COLOR,
        ]
        for colour in colours:
            self.assertEqual(
                len(colour),
                3,
                'Colours should be a length of 3: {}.'.format(colour),
            )

            self.assertIs(
                all(isinstance(col, int) for col in colour),
                True,
                'Colours should be integers: {}.'.format(colour),
            )

            self.assertIs(
                all(-1 < col < 256 for col in colour),
                True,
                'Colours should be value within 0-255: {}.'.format(colour),
            )

    def test_naming_pattern(self):
        self.assertEqual(
            set(crab.config.NAME_PATTERN_GROUPS) == self._available_name_pattern_fields,
            True,
            'All `crab.config.NAME_PATTERN` fields must be '
            'provided in the `crab.config.NAME_PATTERN_GROUPS`.',
        )

    def test_naming_validate_name(self):
        valid_name = crab.config.NAME_PATTERN.format(
            category='CAT',
            counter='001',
            description='description_WITH_0123',
            side='R_B',
        )
        self.assertIs(
            crab.config.validate_name(valid_name),
            True,
            '"{}" should be valid for `crab.config.NAME_PATTERN`.'.format(valid_name),
        )

        invalid_name = crab.config.NAME_PATTERN.format(
            category='$Money',
            counter='Nope',
            description='[desc]',
            side='NoThanks',
        )
        self.assertIs(
            crab.config.validate_name(invalid_name),
            False,
            '"{}" should be invalid for `crab.config.NAME_PATTERN`.'.format(invalid_name),
        )

    def test_naming_get_fields(self):
        valid_name = crab.config.NAME_PATTERN.format(
            category='CAT',
            counter='001',
            description='description_WITH_0123',
            side='R_B',
        )
        self.assertEqual(
            crab.config.get_category(valid_name),
            'CAT',
            '"CAT" should be the category for "{}".'.format(valid_name),
        )
        self.assertEqual(
            crab.config.get_description(valid_name),
            'description_WITH_0123',
            '"description_WITH_0123" should be the description for "{}".'.format(valid_name),
        )
        self.assertEqual(
            crab.config.get_counter(valid_name),
            1,
            '1 should be the counter for "{}".'.format(valid_name),
        )
        self.assertEqual(
            crab.config.get_side(valid_name),
            'R_B',
            '"R_B" should be the side for "{}".'.format(valid_name),
        )
