# run with nose
import VisionEgg
from VisionEgg.Text import Text

def test_dav_obscure_bug():
    # Test a bug reported by Dav Clark. Ported from
    # http://www.freelists.org/archives/visionegg/08-2008/msg00000.html
    s = VisionEgg.Core.Screen()
    t = Text()
    t.set(text='test')
