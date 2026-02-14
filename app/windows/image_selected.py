from windows.selectable_imagebox import SelectableImageBox
from PyQt6.QtCore import QObject

class Image_Selected(QObject):
    def __init__(self, image_box, second_column, parent=None):
        super().__init__(parent)

        image_box.image_selected.connect(self.take_slot)
        self.slot = None

        self.second_column = second_column


    def take_slot(self, slot):
        self.slot = slot

        self.make_event()


    def make_event(self):
        #print("slot:", self.slot)
        #print("index:", self.second_column.index)

        if self.slot == 1:
            if self.second_column.index == 0:
                self.second_column.point_overlay.show()
                
            elif self.second_column.index == 1:
                
                self.remake_grid()

        else:
            if self.second_column.index == 0:
                self.second_column.duped_layer.show()
                
            elif self.second_column.index == 1:
                
                self.remake_grid()



    def remake_grid(self):
        for image in self.second_column.image_array:
            if image["path"] == SelectableImageBox.path[self.slot]:
                number = self.second_column.image_array.index(image)

                if self.slot == 1:
                    self.second_column.grid_overlay.img_arr = self.second_column.image_array[number]["np_array"]

                    self.second_column.grid_overlay.grid_diffs.clear()

                    self.second_column.grid_overlay.resize(self.second_column.image1.size())

                    self.second_column.grid_overlay.calculate_grid()
                    self.second_column.grid_overlay.draw_grid(self.second_column.diff_slider.value())

                    self.second_column.grid_overlay.show()

                else:
                    self.second_column.grid_overlay2.img_arr = self.second_column.image_array[number]["np_array"]

                    self.second_column.grid_overlay2.grid_diffs.clear()

                    self.second_column.grid_overlay2.resize(self.second_column.image2.size())

                    self.second_column.grid_overlay2.calculate_grid()
                    self.second_column.grid_overlay2.draw_grid(self.second_column.diff_slider.value())

                    self.second_column.grid_overlay2.show()
    
        