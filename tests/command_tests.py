from command import escape_name, split_line
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
        outname = escape_name(inname)
        assert_equal(outname, expected)


class TestCommand(object):
    def test_command_split_splits_commands_into_function_args(self):
        line = "my-func arg1 arg2 'arg3'"
        data = split_line(line)
        assert_equal(data[0], 'my-func')
        assert_equal(data[1], 'arg1')
        assert_equal(data[2], 'arg2')
        assert_equal(data[3], "'arg3'")

