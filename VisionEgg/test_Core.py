from VisionEgg.Core import FrameTimer

def test_FrameTimer():
    ft = FrameTimer()
    ft.tick()
    ft.tick()
    result = ft.get_longest_frame_duration_sec()

