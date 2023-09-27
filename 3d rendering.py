import tkinter as tk
from tkinter import ttk
import laspy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class LASViewer:
    def __init__(self, master, las_file_path):
        self.master = master
        self.las_file_path = las_file_path

        # Open the LAS file
        self.lasfile = laspy.open(self.las_file_path, mode="r")
        self.total_points = self.lasfile.header.point_count

        self.all_points = self.lasfile.read()  # Svarbu skaityti duomenis prieš juos naudojant!

        x_values = self.all_points['X']
        y_values = self.all_points['Y']
        z_values = self.all_points['Z']

        self.x_min, self.x_max = x_values.min(), x_values.max()
        self.y_min, self.y_max = y_values.min(), y_values.max()
        self.z_min, self.z_max = z_values.min(), z_values.max()

        # GUI Elements
        self.label_total_points = ttk.Label(master, text=f"Total points in file: {self.total_points}")
        self.label_total_points.pack()

        self.label_bounds = ttk.Label(master,
                                      text=f"Bounds (X: {self.x_min}-{self.x_max}, Y: {self.y_min}-{self.y_max}, Z: {self.z_min}-{self.z_max})")
        self.label_bounds.pack()

        self.options = [8, 64, 512, 4096]
        for option in self.options:
            btn = ttk.Button(master, text=f"x,y(1 of {option})", command=lambda o=option: self.set_division(o))
            btn.pack()

        self.btn_square = ttk.Button(master, text="Square Representation", command=lambda: self.set_representation("square"))
        self.btn_square.pack()

        self.btn_circular = ttk.Button(master, text="Circular Rendering", command=lambda: self.set_representation("circular"))
        self.btn_circular.pack()

        self.representation_mode = "square"  # pradinė reikšmė

        self.label_selected_division = ttk.Label(master, text="Selected division: N/A")
        self.label_selected_division.pack()

        self.label_x_area = ttk.Label(master, text="x area:")
        self.label_x_area.pack()
        self.entry_x_area = ttk.Entry(master)
        self.entry_x_area.pack()

        self.label_y_area = ttk.Label(master, text="y area:")
        self.label_y_area.pack()
        self.entry_y_area = ttk.Entry(master)
        self.entry_y_area.pack()

        self.btn_show = ttk.Button(master, text="Atvaizduoti taskus", command=self.plot_points)
        self.btn_show.pack()

        self.label_final_selection = ttk.Label(master, text="Final selection: N/A")
        self.label_final_selection.pack()

        self.current_division = None

        self.x_values = self.all_points['X']
        self.y_values = self.all_points['Y']
        self.z_values = self.all_points['Z']

        self.x_min, self.x_max = self.x_values.min(), self.x_values.max()
        self.y_min, self.y_max = self.y_values.min(), self.y_values.max()
        self.z_min, self.z_max = self.z_values.min(), self.z_values.max()

    def set_representation(self, mode):
        #Nustatyti atvaizdavimo būdą ("square" arba "circular")
        self.representation_mode = mode

    def set_division(self, option):
        self.current_division = option
        self.label_selected_division.config(text=f"Selected division: 1/{option}")

    def plot_points(self):
        # Paimkime pasirinktą x, y sritį
        x_area = int(self.entry_x_area.get())
        y_area = int(self.entry_y_area.get())

        x_range = (self.x_max - self.x_min) / self.current_division
        y_range = (self.y_max - self.y_min) / self.current_division

        x_start = self.x_min + x_range * (x_area - 1)
        x_end = x_start + x_range

        y_start = self.y_min + y_range * (y_area - 1)
        y_end = y_start + y_range

        # Filtruojame taškus pagal kvadratinę sritį
        mask = (self.all_points['X'] >= x_start) & (self.all_points['X'] <= x_end) & \
                (self.all_points['Y'] >= y_start) & (self.all_points['Y'] <= y_end)
        filtered_points = self.all_points[mask]

        # Jei atvaizdavimo būdas yra "circular", taikome papildomą filtrą
        if self.representation_mode == "circular":
            x_center = (x_start + x_end) / 2
            y_center = (y_start + y_end) / 2
            radius_sq = (x_range / 2) ** 2  # Priklauso nuo to, kiek jums reikia spindulio

            circular_mask = ((filtered_points['X'] - x_center) ** 2 + (
                        filtered_points['Y'] - y_center) ** 2) <= radius_sq
            filtered_points = filtered_points[circular_mask]

        # "Final selection: N/A" = last pick
        final_selection_text = f"Last selection: x,y(1 of {self.current_division}), x area: {x_area}, y area: {y_area}"
        self.label_final_selection.config(text=final_selection_text)

        # Dabar galite naudoti filtered_points kintamąjį, kad sukurtumėte 3D plot'ą
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        scatter = ax.scatter(filtered_points['X'], filtered_points['Y'], filtered_points['Z'],
                                c=filtered_points['Z'], cmap=plt.get_cmap('viridis'))
        fig.colorbar(scatter)

        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        ax.set_title('3D LAS Points Visualization')

        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    viewer = LASViewer(root, "2743_1234.las")
    root.mainloop()



