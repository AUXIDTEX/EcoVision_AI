import numpy as np

class Average_color:
    def __init__(self, image_arr, label_width, label_height):
        self.img_arr = image_arr
        self.label_w = label_width
        self.label_h = label_height


    def calculate(self, x, y, rad):
        h, w, _ = self.img_arr.shape

        scale_x = w / self.label_w
        scale_y = h / self.label_h
            
        real_x = int(x * scale_x)
        real_y = int(y * scale_y)

        x_min = max(real_x - rad, 0)
        x_max = min(real_x + rad, w)
        y_min = max(real_y - rad, 0)
        y_max = min(real_y + rad, h)

        region = self.img_arr[y_min:y_max + 1, x_min:x_max + 1, :]
        avg_chanel = np.mean(region, axis=(0, 1))

        avg_color = tuple(avg_chanel.astype(int))
        return avg_color