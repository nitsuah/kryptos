from kryptos.cli import main


def test_cli_sections(capsys):
    code = main(["sections"])
    assert code == 0
    out = capsys.readouterr().out
    assert "K1" in out and "K4" in out
