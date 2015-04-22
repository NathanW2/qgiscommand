from ..command import escape_name, split_line
from nose.tools import assert_equal

from .. import command


@command.command(alias='test')
def test_command():
    """
    Test Command Help
    """
    pass


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

    def test_alias_should_have_same_help_and_source(self):
        help1 = command.help_text['test-command']
        help2 = command.help_text['test']
        source1 = command.sourcelookup['test-command']
        source2 = command.sourcelookup['test']
        assert_equal(help1, help2)
        assert_equal(source1, source2)
