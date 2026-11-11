from engine.profiles import list_profiles, load_profile


def test_all_five_profiles_load_and_validate():
    profiles = list_profiles()
    assert len(profiles) == 5
    assert all(profile["dpi"] == 1200 for profile in profiles)


def test_profile_pixel_dimensions():
    expected = {
        "fat_250ml": (9000, 2400),
        "fat_500ml": (9000, 6000),
        "fat_1l": (12000, 6000),
        "long_500ml": (9000, 4560),
        "long_1l": (12000, 6000),
    }
    for profile_id, dimensions in expected.items():
        profile = load_profile(profile_id)
        assert (profile["width_px"], profile["height_px"]) == dimensions


def test_profiles_are_black_and_white():
    assert all(p["artwork_color"] == "black-and-white" for p in list_profiles())
