from libc.math cimport cos, sin, M_PI
# import the python objects
# (some items are python functions or types only)
import dearcygui as dcg
# cimport is needed to access dcg fields and subclass draw
cimport dearcygui as dcg
from cpython.time cimport time

cdef class CircleLinesMonolithic(dcg.drawingItem):
    """Draws lines connecting points on a circle using a single draw call."""
    cdef unsigned int color
    cdef dcg.Vec2 center
    cdef float thickness
    cdef float radius
    cdef int num_points
    
    def __init__(self, context, float radius=100.0, int num_points=8, 
                 center=(0.0, 0.0), color=(0, 0, 255), thickness=1.0):
        super().__init__(context)
        self.radius = radius
        self.num_points = num_points if num_points > 2 else 3
        self.center = dcg.make_Vec2(center[0], center[1])  
        self.color = dcg.color_as_int(color)
        self.thickness = thickness

    cdef void draw(self, void* draw_list) noexcept nogil:
        cdef int i, j
        cdef float angle1, angle2
        cdef float x1, y1, x2, y2
        cdef float two_pi = 2 * M_PI
        cdef float thickness = self.thickness * self.context.viewport.thickness_multiplier
        if thickness > 0:
            thickness *= self.context.viewport.size_multiplier
        thickness = abs(thickness)
        
        # Draw lines between all point combinations
        for i in range(self.num_points):
            angle1 = two_pi * i / self.num_points
            x1 = self.center.x + self.radius * cos(angle1)
            y1 = self.center.y + self.radius * sin(angle1)
            
            for j in range(i + 1, self.num_points):
                angle2 = two_pi * j / self.num_points
                x2 = self.center.x + self.radius * cos(angle2)
                y2 = self.center.y + self.radius * sin(angle2)
                
                dcg.imgui.draw_line(self.context,
                                    draw_list, 
                                    x1, y1,
                                    x2, y2, 
                                    self.color, 
                                    thickness)

class CircleLinesList(dcg.DrawingList):
    """Creates the same visual result by managing multiple DrawLine items."""
    
    def __init__(self, context, float radius=100.0, int num_points=8,
                 center=(0.0, 0.0), color=(0, 0, 255), thickness=1.0):
        super().__init__(context)
        
        cdef int i, j
        cdef float angle1, angle2
        cdef float x1, y1, x2, y2
        cdef float two_pi = 2 * M_PI
        cdef float xc, yc
        xc = center[0]
        yc = center[1]
        
        # Draw lines between all point combinations
        for i in range(num_points):
            angle1 = two_pi * i / num_points
            x1 = xc + radius * cos(angle1)
            y1 = yc + radius * sin(angle1)
            
            for j in range(i + 1, num_points):
                angle2 = two_pi * j / num_points
                x2 = xc + radius * cos(angle2)
                y2 = yc + radius * sin(angle2)
                dcg.DrawLine(context,
                             p1=(x1, y1),
                             p2=(x2, y2),
                             parent=self,
                             color=color,
                             thickness=thickness)


cdef class BenchmarkDrawInWindow(dcg.DrawInWindow):
    """ A DrawInWindow that benchmarks the time it
    takes to render its children """
            
    def __cinit__(self):
        self._value = dcg.SharedDouble(self.context, 0.0) # running time average in ms

    @property
    def value(self) -> dcg.SharedDouble:
        return self._value

    cdef void draw(self) noexcept nogil:
        cdef double start_time, end_time
        start_time = time()
        dcg.DrawInWindow.draw(self)
        end_time = time()
        cdef double cur = dcg.SharedDouble.get(<dcg.SharedDouble>self._value)
        cur = cur * 0.9 + 0.1 * (end_time - start_time) * 1000
        dcg.SharedDouble.set(<dcg.SharedDouble>self._value, cur)

