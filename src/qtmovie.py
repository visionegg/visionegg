"""high level QuickTime Movie wrapper"""
import qtlowlevel
import ctypes

qtlowlevel.InitializeQTML(0)
qtlowlevel.EnterMovies()

def new_movie_from_filename(filename, MAX_PATH=255):
    """create a Movie from filename"""
    movieProps = (qtlowlevel.QTNewMoviePropertyElement * 5)()
    filename = unicode(filename)

    movieFilePathRef = qtlowlevel.CFStringRef()
    movieFilePathRef.value = qtlowlevel.CFStringCreateWithCharacters(qtlowlevel.kCFAllocatorDefault,
                                                                     filename,
                                                                     len(filename))

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

class Rect:
    def __init__(self,top=0,left=0,bottom=0,right=0):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

class Movie:
    """An encapsulated QuickTime Movie"""
    def __init__(self,theMovie):
        self.theMovie = theMovie
    def GetMovieBox(self):
        movieBounds = qtlowlevel.Rect()
        qtlowlevel.GetMovieBox(self.theMovie, ctypes.byref(movieBounds))
        return Rect(top=movieBounds.top,
                    left=movieBounds.left,
                    bottom=movieBounds.bottom,
                    right=movieBounds.right)
    
    def SetMovieBox(self,bounds):
        if not isinstance(bounds,Rect):
            raise ValueError('bounds argument must be instance of VisionEgg.qtmovie.Rect')
        b = qtlowlevel.Rect()
        (b.top, b.left, b.bottom, b.right) = (bounds.top, bounds.left,
                                              bounds.bottom, bounds.right)
        qtlowlevel.SetMovieBox(self.theMovie, ctypes.byref(b))
    def StartMovie(self):
        qtlowlevel.StartMovie(self.theMovie)

    def MoviesTask(self,value):
        qtlowlevel.MoviesTask(self.theMovie, value)

    def IsMovieDone(self):
        return qtlowlevel.IsMovieDone(self.theMovie)

    def GoToBeginningOfMovie(self):
        qtlowlevel.GoToBeginningOfMovie(self.theMovie)
