from modules.selectable_imagebox import SelectableImageBox
from PyQt6.QtWidgets import QMessageBox

def switch_modes(second_column, index):
        second_column.index = index

        ai = second_column.ai_module



        mode_changed = index != second_column.mode
        if second_column.mode == 2 and index != 2:
            ai.stop_ai_inference()
            ai.stop_ai_folder_processing()





        if index == 0 and second_column.image_array:
            second_column.mode = 0
            #POINT MODE

            if mode_changed:
                second_column.clear_selected_images()

            ai.vertical_ai_widget.hide()
            second_column.spectral_filterer.hide()

            second_column.image_widget.show()
            second_column.color_title.show()
            second_column.color_widget.show()

            ai.ai_image_box.hide()


            second_column.grid_overlay.hide()
            second_column.grid_overlay2.hide()

            second_column.compare_title.setText("Режим точок")

            for widget in second_column.output_widgets:
                widget.show()
            
            for frame in second_column.mesh_arr:
                frame.deleteLater()
            second_column.mesh_arr.clear()

            second_column.settings_widget.show()

            second_column.slider_widget.show()
            second_column.diff_widget.hide()
            second_column.sizer_widget.hide()


            if second_column.image1.show() == True:
              second_column.point_overlay.show()

            if second_column.image2.show() == True:
                second_column.duped_layer.show()


            second_column.window.update()





        elif index == 1 and second_column.image_array:
            second_column.mode = 1
            #GRID MODE 

            if mode_changed:
                second_column.clear_selected_images()

            ai.vertical_ai_widget.hide()
            second_column.spectral_filterer.hide()

            second_column.image_widget.show()
            second_column.color_title.show()
            second_column.color_widget.show()

            ai.ai_image_box.hide()

            second_column.compare_title.setText("Режим сітки")

            second_column.point_overlay.hide()
            second_column.duped_layer.hide()

            second_column.grid_overlay.show()
            second_column.grid_overlay2.show()

            second_column.update_grid_paths()

            second_column.grid_overlay.draw_grid(second_column.diff_slider.value())
            second_column.grid_overlay2.draw_grid(second_column.diff_slider.value())
                
            second_column.settings_widget.show()

            second_column.slider_widget.hide()
            second_column.diff_widget.show()
            second_column.sizer_widget.show()

            for widget in second_column.output_widgets:
                widget.hide()

            second_column.window.update()






        elif index == 2 and second_column.image_array:
            second_column.mode = 2
            #NEURAL NETWORK MODE

            second_column.image_widget.hide()
            second_column.color_title.hide()
            second_column.color_widget.hide()
            second_column.spectral_filterer.hide()

            second_column.compare_title.setText("Режим нейромережі")

            second_column.settings_widget.hide()

            ai.vertical_ai_widget.show()
            ai.mode_switch_func("1" if ai.file_mode_label.isChecked() else "2")

            if ai.file_mode_label.isChecked():
                index = 1
                if SelectableImageBox.path[1] is None:
                    index = 2
                ai.start_ai_inference(SelectableImageBox.path[index])
                ai.ai_image_box.show()

            second_column.window.update()





        elif index == 3 and second_column.image_array:
            second_column.mode = 3
            #SPECTRAL FILTERER MODE

            if mode_changed:
                second_column.clear_selected_images()

            second_column.image_widget.hide()
            second_column.color_title.hide()
            second_column.color_widget.hide()

            ai.vertical_ai_widget.hide()
            ai.ai_image_box.hide()
            second_column.spectral_filterer.show()

            second_column.settings_widget.hide()

            second_column.compare_title.setText("Режим фільтрування зображень")
            
            second_column.spectral_filterer.set_image()

            second_column.window.update()

        else:
            QMessageBox.warning(second_column, "Попередження", "Будь ласка, виберіть два зображення для порівняння.")
            second_column.mode_selection.blockSignals(True)
            second_column.mode_selection.setCurrentIndex(second_column.mode)
            second_column.mode_selection.blockSignals(False)