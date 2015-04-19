from command import escape_name
from nose.tools import assert_equal


class TestCommandNaming(object):
    def test_escape_name_should_replace_underscore_with_dash(self):
        inname = "test_name"
        expected = "test-name"
        outname = escape_name(inname)
        assert_equal(outname, expected)

    def test_escape_name_should_replace_space_with_dash(self):
        inname = "test name"
        expected = "test-name"
        outname = escape_name(inname)
        assert_equal(outname, expected)

    def test_escape_name_should_should_lower_case(self):
        inname = "TEST NAME"
        expected = "test-name"
        outname = escape_eame(inname)
        assert_equal(outname, expected)
