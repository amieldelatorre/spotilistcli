import commands


def test_get_usage(monkeypatch):
    monkeypatch.setattr(commands, "top_level_command_args", {
        "something1": None,
        "something2": None,
        "something3": None
    })

    result = commands.get_usage()
    assert result == "usage: spotiList {help,configure,something1,something2,something3}"
