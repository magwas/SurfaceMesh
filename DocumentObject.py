import FreeCAD
import warnings

class DocumentObject(object):
    def __init__(self):
        object.__setattr__(self,'__object__',None)
        object.__setattr__(self,'__vobject__',None)

    def __getattr__(self,name):
        try:
            return getattr(self.__object__,name)
        except AttributeError:
            pass
        return getattr(self.__vobject__,name)
        
    def __setattr__(self,name,value):
        try:
            setattr(self.__object__,name,value)
            return
        except AttributeError:
            pass
        try:
            setattr(self.__vobject__,name,value)
            return
        except AttributeError:
            pass
        object.__setattr__(self, name, value)
        
    def getobj(self):
        warnings.warn("getobj should not exist", DeprecationWarning)
        return self.__object__

    def getvobj(self):
        warnings.warn("getcobj should not exist", DeprecationWarning)
        return self.__vobject__

    def onChanged(self,prop):
        return

    def attach(self):
        FreeCAD.Console.PrintMessage("attached %s\n"%(self.Object.Label))
        return

    def execute(self):
        return

