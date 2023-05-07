import pyglet
from constants import batch

# structure form assignment1
class Rect:
    rectangles = []

    def __init__(self, x, y, width=66, height=33):
        self.x = x
        self.y = y
        self.color = (255, 0, 0)  # standard color
        self.checked_color = (0, 255, 0)  # color when checked
        self.shape = pyglet.shapes.Rectangle(self.x, self.y, width, height, color=self.color, batch=batch)
        self.checked = False

    def draw_rects():
        for rect in Rect.rectangles:
            rect.draw()

    def create_rect(x, y):
        Rect.rectangles.append(Rect(x, y))


    def change_check(self):
        if self.checked:
            self.checked = False
            self.shape.color = self.color
        else:
            self.checked = True
            self.shape.color = self.checked_color
        Rect.draw_rects()

    def get_index_of_checked():
        for rect in Rect.rectangles:
            if rect.checked:
                for i in range(len(Rect.rectangles)):
                    if Rect.rectangles[i] == rect:
                        return i

    def draw(self):
        self.shape.draw()

