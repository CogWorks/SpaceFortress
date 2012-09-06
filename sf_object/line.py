#line.py
#this code is to be placed in the "sf_object" subfolder
#Pygame Space Fortress
#Marc Destefano
#Rensselaer Polytechnic Institute
#Fall 2008
from __future__ import division

class Line(object):
    """A Line. Seriously"""
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        super(Line, self).__init__()
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self._WITHIN_BOUNDS = -10000.0 #below ranges for drawing
        
    def __eq__(self, other):
        """sets a line equal to another line"""
        other.x1 = self.x1
        other.x2 = self.x2
        other.y1 = self.y1
        other.y2 = self.y2
        
    def scale_line(self, xscalefactor, yscalefactor):
        """scales a line by two dimensional constants"""
        self.x1 *= xscalefactor
        self.x2 *= xscalefactor
        self.y1 *= yscalefactor
        self.y2 *= yscalefactor
        
    
    def shift_line(self, xshiftfactor, yshiftfactor):
        """moves a line by two dimensional constants"""
        self.x1 += xshiftfactor
        self.x2 += xshiftfactor
        self.y1 += yshiftfactor
        self.y2 += yshiftfactor
        
    def check_bounds(self, num, lowerbound, upperbound):
        """Checks the Bounds. This is useful, isn't it?"""
        if num < lowerbound:
            return lowerbound
        if num > upperbound:
            return upperbound
        else:
            return self._WITHIN_BOUNDS
            
    def clip_line(self, leftbound, topbound, rightbound, botbound):
        """Doesn't draw the whole line if we're at an edge or something"""
        dy = self.y2 - self.y1
        dx = self.x2 - self.x1
        newx1 = self.x1
        newx2 = self.x2
        newy1 = self.y1
        newy2 = self.y2
        b = 0.0
       
        if dx != 0:
            b = self.check_bounds(self.x1, leftbound, rightbound)
            if b != self._WITHIN_BOUNDS:
                newy1 = self.y2 - (self.x2 -b) * (dy / dx)
                newx1 = b
            b = self.check_bounds(self.x2, leftbound, rightbound)
            if b != self._WITHIN_BOUNDS:
                newy2 = self.y1 - (self.x1 - b) * (dy / dx)
                newx2 = b
           
        if dy != 0:
            b = self.check_bounds(self.y1, topbound, botbound)
            if b != self._WITHIN_BOUNDS:
                newx1 = self.x2 - (self.y2 - b) * (dx / dy)
                newy1 = b
            b = self.check_bounds(self.y2, topbound, botbound)
            if b != self._WITHIN_BOUNDS:
                newx2 = self.x1 - (self.y1 - b) * (dx / dy)
                newy2 = b
        
        self.x1 = newx1
        self.x2 = newx2
        self.y1 = newy1
        self.y2 = newy2
        
if __name__ == '__main__':
    l1 = Line(5,3,10,10)
    l2 = l1
    print l1.x1, l2.x1
    l1.clip_line(0,5,5,0)
    print l1.x1, l1.y1, l1.x2, l1.y2

         