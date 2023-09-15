#### Custom Viewport Overlay ####
# Description of your Python-based viewport layer.

from ovito.vis import *
from ovito.data import *

class ViewportOverlayName(ViewportOverlayInterface):

    def render(self, canvas: ViewportOverlayInterface.Canvas, data: DataCollection, frame: int, **kwargs):

        # [[Replace the following demo code with your own implementation]]

        # Access the data collection computed by the pipeline
        num_particles = data.particles.count if data and data.particles else 0
        text = f"Hello world, the system contains {num_particles} particles"

        # Draw some text using the Canvas.draw_text() method
        canvas.draw_text(text, pos=(0.5, 0.5), anchor="center", outline_width=2)

        # Draw an ellipse using a QPainter object, which is created by Canvas.qt_painter()
        with canvas.qt_painter() as painter:
            painter.drawEllipse(painter.window())
