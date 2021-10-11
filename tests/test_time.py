import a0


def test_time():
    mono_now = a0.TimeMono.now()
    assert len(str(mono_now)) == 19
    assert str(mono_now) == str(a0.TimeMono.parse(str(mono_now)))

    wall_now = a0.TimeWall.now()
    assert len(str(wall_now)) == 35
    assert str(wall_now).endswith("-00:00")
    assert str(wall_now) == str(a0.TimeWall.parse(str(wall_now)))
