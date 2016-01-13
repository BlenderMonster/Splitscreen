from mutil import sensors
from mbge import context, render

PROPERTY_LAYOUT = "layout"
'Layout string e.g. "v(1, 2)" for vertical split viewport 1 and 2.'
PROPERTY_VIEWPORT = "viewport"
'Property containing the key of the viewport to be used at'

def setup():
    if not sensors.allPositive:
        return
    
    layout = context.owner[PROPERTY_LAYOUT]
    eval(layout, saveGlobals()).createViewports()
    

def findCamera(key):
    cameras = [camera for camera in context.scene.cameras 
            if camera.get(PROPERTY_VIEWPORT) == key ]
    if not cameras:
        raise SearchError("No camera with property '{}' = {} found in scene {}".format(
                            PROPERTY_VIEWPORT, key, context.scene.name))
    camera = cameras[0]
    if len(cameras)>1:
        print("Warning: more than one camera with property '{}' = {} found in scene {}: {} - use {}".format(
               PROPERTY_VIEWPORT, key, context.scene.name, cameras, camera))
    return camera

def saveGlobals():
    return {"v":VerticalViewport, "h":HorizontalViewport}

class SearchError(Exception):
    pass
        
class Viewport:
    def __init__(self, *components):
        self.components = components
        for component in components:
            if isinstance(component, Viewport):
                component.parent = self
    
    def createViewports(self, canvas = None):
        self.setupCanvas(canvas)
        
        for index in range(len(self.components)):            
            self.createComponentViewport(index)
    
    def createComponentViewport(self, index):
        componentCanvas = self.createComponentCanvas(index)
        component = self.components[index]
        if isinstance(component, Viewport):
            component.createViewports(componentCanvas)
        else:
            self.createCameraViewport(component, componentCanvas)
                    
    def setupCanvas(self, canvas):
        if not canvas:
            self.canvas = Canvas(0, 0, render.width, render.height)
        else:
            self.canvas = canvas
        
    def createCameraViewport(self, key, canvas):
        camera = findCamera(key)
        camera.setViewport(canvas.x, canvas.y, canvas.width, canvas.height)
        camera.useViewport = True
        
class VerticalViewport(Viewport):
    def createComponentCanvas(self, index):
        numComponents = len(self.components)
        height = (self.canvas.height - self.canvas.y)/numComponents
        orderedIndex = numComponents - 1 - index
        print(orderedIndex)
        return Canvas(
                self.canvas.x, int(height * orderedIndex),
                self.canvas.width, int(height * (orderedIndex + 1)))

class HorizontalViewport(Viewport):
    def createComponentCanvas(self, index):
        numComponents = len(self.components)
        width = (self.canvas.width - self.canvas.x)/numComponents
        return Canvas(
                int(width * index), self.canvas.y, 
                int(width * (index + 1)), self.canvas.height)

class Canvas:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def __str__(self):
        return "[x:{}, y:{}; w:{}, h:{}]".format(
                self.x, self.y, self.width, self.height)