"""high level QuickTime wrapper"""
import qtlowlevel
import ctypes

qtlowlevel.InitializeQTML(0)
qtlowlevel.EnterMovies()

def new_movie_from_filename(filename, MAX_PATH=255):
    movieProps = (qtlowlevel.QTNewMoviePropertyElement * 5)()
    filename = unicode(filename)

    movieFilePathRef = qtlowlevel.CFStringRef()
    if 1:
        c_filename = ctypes.c_char_p(str(filename))
        print 'c_filename',c_filename
        movieFilePathRef.value = qtlowlevel.CFStringCreateWithCString(None,
                                                                c_filename,
                                                                qtlowlevel.kCFStringEncodingMacRoman)
    else:
        # unicode filenames not working for some reason
        wc_filename = ctypes.c_wchar_p(filename)
        print 'wc_filename',wc_filename
        movieFilePathRef.value = qtlowlevel.CFStringCreateWithCharacters(qtlowlevel.kCFAllocatorDefault,
                                                                   wc_filename,
                                                                   MAX_PATH)

    if 1:
        print 'movieFilePathRef',movieFilePathRef
        buf = ctypes.create_string_buffer(MAX_PATH)
        qtlowlevel.CFStringGetCString( movieFilePathRef,
                                 buf,
                                 MAX_PATH,
                                 qtlowlevel.kCFStringEncodingMacRoman)
        print 'buf',buf.raw

    moviePropCount = 0

    movieProps[moviePropCount].propClass = qtlowlevel.kQTPropertyClass_DataLocation
    movieProps[moviePropCount].propID = qtlowlevel.kQTDataLocationPropertyID_CFStringWindowsPath
    movieProps[moviePropCount].propValueSize = ctypes.sizeof(ctypes.c_void_p)
    movieProps[moviePropCount].propValueAddress = ctypes.cast(ctypes.byref(movieFilePathRef),ctypes.c_void_p)
    movieProps[moviePropCount].propStatus = 0

    moviePropCount += 1

    boolTrue = ctypes.c_ubyte(1)
    movieProps[moviePropCount].propClass = qtlowlevel.kQTPropertyClass_MovieInstantiation
    movieProps[moviePropCount].propID = qtlowlevel.kQTMovieInstantiationPropertyID_DontAskUnresolvedDataRefs
    movieProps[moviePropCount].propValueSize = ctypes.sizeof(boolTrue)
    movieProps[moviePropCount].propValueAddress = ctypes.cast(ctypes.pointer(boolTrue),ctypes.c_void_p)
    movieProps[moviePropCount].propStatus = 0

    moviePropCount += 1

    movieProps[moviePropCount].propClass = qtlowlevel.kQTPropertyClass_NewMovieProperty
    movieProps[moviePropCount].propID = qtlowlevel.kQTNewMoviePropertyID_Active
    movieProps[moviePropCount].propValueSize = ctypes.sizeof(boolTrue)
    movieProps[moviePropCount].propValueAddress = ctypes.cast(ctypes.pointer(boolTrue),ctypes.c_void_p)
    movieProps[moviePropCount].propStatus = 0

    moviePropCount += 1

    movieProps[moviePropCount].propClass = qtlowlevel.kQTPropertyClass_NewMovieProperty
    movieProps[moviePropCount].propID = qtlowlevel.kQTNewMoviePropertyID_DontInteractWithUser
    movieProps[moviePropCount].propValueSize = ctypes.sizeof(boolTrue)
    movieProps[moviePropCount].propValueAddress = ctypes.cast(ctypes.pointer(boolTrue),ctypes.c_void_p)
    movieProps[moviePropCount].propStatus = 0

    moviePropCount += 1

    theMovie = qtlowlevel.Movie()
    qtlowlevel.NewMovieFromProperties( moviePropCount, movieProps, 0, None, ctypes.byref(theMovie))
    return Movie(theMovie)

class Movie:
    def __init__(self,theMovie):
        self.theMovie = theMovie
    def GetMovieBox(self):
        movieBounds = qtlowlevel.Rect()
        qtlowlevel.GetMovieBox(self.theMovie, ctypes.byref(movieBounds))
        return (movieBounds.top,
                movieBounds.left,
                movieBounds.bottom,
                movieBounds.right)
    
    def SetMovieBox(self,bounds):
        b = qtlowlevel.Rect()
        (b.top, b.left, b.bottom, b.right) = bounds
        qtlowlevel.SetMovieBox(self.theMovie, ctypes.byref(b))
