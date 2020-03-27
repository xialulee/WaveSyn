import PIL
from PIL import ImageTk
from PIL import Image



class ArrayRenderMixin:
    def render_array(self, arr, image_id=None):
        image   = Image.fromarray(arr)
        photoImage   = ImageTk.PhotoImage(image=image)

        if not image_id:
            image_id  = self.create_image((0, 0), image=photoImage, anchor='nw')
        else:
            self.itemconfig(image_id, image=photoImage)
        return image_id, photoImage
