from pathlib import Path

import pytest

from litestar.utils.version import Version, get_version, parse_version


@pytest.mark.parametrize(
    "raw_version,expected",
    [
        ("2.0.0alpha1", Version(2, 0, 0, "alpha", 1)),
        ("2.0.0a1", Version(2, 0, 0, "alpha", 1)),  # test importlib.metadata.version coercion
        ("2.0.0alpha2", Version(2, 0, 0, "alpha", 2)),
        ("2.0.0beta1", Version(2, 0, 0, "beta", 1)),
        ("2.0.0b1", Version(2, 0, 0, "beta", 1)),  # test importlib.metadata.version coercion
        ("2.0.0beta2", Version(2, 0, 0, "beta", 2)),
        ("2.0.0rc1", Version(2, 0, 0, "rc", 1)),
        ("2.0.0rc2", Version(2, 0, 0, "rc", 2)),
        ("2.0.0", Version(2, 0, 0, "final", 0)),
        ("2.13.45", Version(2, 13, 45, "final", 0)),
        ("1.2.3.alpha1", Version(1, 2, 3, "alpha", 1)),
        ("1.2.3.alpha.1", Version(1, 2, 3, "alpha", 1)),
        ("1.2.3b.1", Version(1, 2, 3, "beta", 1)),
        ("\uff11.\uff12.\uff13", Version(1, 2, 3, "final", 0)),
        ("1..2..3", Version(1, 2, 3, "final", 0)),
        ("1.2.3.dev1", Version(1, 2, 3, "final", 0)),
        ("1.2.3.dev", Version(1, 2, 3, "final", 0)),
        ("1.2.3+local", Version(1, 2, 3, "final", 0)),
        ("1.2.3+abc.123", Version(1, 2, 3, "final", 0)),
        ("1.2.3+abc-123_xyz", Version(1, 2, 3, "final", 0)),
        ("1.2.3.post1", Version(1, 2, 3, "final", 0)),
        ("1.2.3.post", Version(1, 2, 3, "final", 0)),
        ("1.2.3.post1.dev2+local", Version(1, 2, 3, "final", 0)),
        ("1.2.3b1.dev2+abc", Version(1, 2, 3, "beta", 1)),
        ("1.2.3rc2.post1.dev3+local", Version(1, 2, 3, "rc", 2)),
        ("1.2.3B1.DEV2+ABC", Version(1, 2, 3, "beta", 1)),
    ],
)
def test_parse_version(raw_version: str, expected: Version) -> None:
    assert parse_version(raw_version) == expected


@pytest.mark.parametrize(
    "raw_version,expected",
    [
        ("1.2.3.dev1", Version(1, 2, 3, "final", 0)),
        ("1.2.3+local", Version(1, 2, 3, "final", 0)),
        ("1.2.3b1.dev2+abc", Version(1, 2, 3, "beta", 1)),
    ],
)
def test_get_version(raw_version: str, expected: Version, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    distribution = tmp_path / f"litestar-{raw_version}.dist-info"
    distribution.mkdir()
    (distribution / "METADATA").write_text(f"Metadata-Version: 2.1\nName: litestar\nVersion: {raw_version}\n")
    monkeypatch.syspath_prepend(str(tmp_path))

    assert get_version() == expected


@pytest.mark.parametrize(
    "raw_version",
    [
        "0.1",
        "1.0.0foo1",
        "1.0.0alpha",
        "1.0.0.0",
        "1.2.3.devx",
        "1.2.3.postx",
        "1.2.3+",
        "1.2.3+abc..def",
        "1.2.3+abc!",
        "1.2.3.dev1.post1",
        "1.2.3b1garbage",
        "1.2.3\n",
    ],
)
def test_parse_invalid_version(raw_version: str) -> None:
    with pytest.raises(ValueError):
        parse_version(raw_version)


@pytest.mark.parametrize(
    "raw_version,message",
    [("1.0.0foo1", "Invalid release level: foo"), ("0.1", "Invalid version: 0.1")],
)
def test_parse_invalid_version_message(raw_version: str, message: str) -> None:
    with pytest.raises(ValueError) as exc_info:
        parse_version(raw_version)
    assert str(exc_info.value) == message


@pytest.mark.parametrize("short,expected_output", [(True, "2.0.0"), (False, "2.0.0alpha1")])
def test_formatted(short: bool, expected_output: str) -> None:
    assert parse_version("2.0.0alpha1").formatted(short=short) == expected_output
