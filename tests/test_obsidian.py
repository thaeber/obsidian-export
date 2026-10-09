from obsidian_export.obsidian import _decode_command_output


def test_decode_command_output_replaces_invalid_utf8_bytes() -> None:
    raw = b'bad\x81text'

    assert _decode_command_output(raw) == 'bad�text'
