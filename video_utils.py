import numpy, cv
from pygame import surfarray

def NumPy2Ipl(input):
    
    if not isinstance(input, numpy.ndarray):
        raise TypeError, 'Must be called with numpy.ndarray!'
    
    ndim = input.ndim
    if not ndim in (2, 3):
        raise ValueError, 'Only 2D-arrays and 3D-arrays are supported!'
    
    if ndim == 2:
        channels = 1
    else:
        channels = input.shape[2]
    
    if input.dtype == numpy.uint8:
        depth = cv.IPL_DEPTH_8U
    elif input.dtype == numpy.float32:
        depth = cv.IPL_DEPTH_32F
    elif input.dtype == numpy.float64:
        depth = cv.IPL_DEPTH_64F
    
    modes_list = [(1, numpy.uint8), (3, numpy.uint8), (1, numpy.float32), (1, numpy.float64)]
    
    if not (channels, input.dtype) in modes_list:
        raise ValueError, 'Unknown or unsupported input mode'
    
    bgr = cv.CreateImageHeader((input.shape[1], input.shape[0]), depth, channels)
    cv.SetData(bgr, input.tostring())
    
    rgb = cv.CreateImage((input.shape[1], input.shape[0]), depth, channels)
    cv.CvtColor(bgr, rgb, cv.CV_BGR2RGB) 
    
    return rgb

def surf2CV(surf):
    
    numpyImage = surfarray.pixels3d(surf)
    cvImage = NumPy2Ipl(numpyImage.transpose(1, 0, 2))
    
    return cvImage
