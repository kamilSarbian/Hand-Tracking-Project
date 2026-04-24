import re

from utils.file_utils import generate_timestamp_filename


def test_generate_timestamp_filename_uses_microseconds():
    filename = generate_timestamp_filename("screenshot", "png")

    assert re.fullmatch(r"screenshot_\d{8}_\d{6}_\d{6}\.png", filename)
