from pytest import CaptureFixture

from mkdocs_editor_notes.main import main


def test_raise(capsys: CaptureFixture[str]):
    main()
    assert "Ritchie Blackmore" in capsys.readouterr().out
