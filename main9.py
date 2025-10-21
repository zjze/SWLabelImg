#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : 补充尾迹修改尺寸和标注
@File ：main9.py
@Auth ： zjz
@Data ： 2024/7/8 15:54
"""

"""角度调整"""
import tkinter as tk
from tkinter import filedialog, Frame, Button, Listbox
from PIL import Image, ImageTk
import xml.etree.ElementTree as ET
import math
import os
import glob
# os.system("pause")
class ImageAnnotationApp:
    def __init__(self, master):
        self.master = master
        # self.master.title("ShipWakeLabelImg")
        self.master.title("SWLabelImg")
        self.master.iconbitmap("./icons/expert2.ico")  # Set the icon to expert2.ico

        # Creating a menu bar
        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.load_image_directory)
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Edit")
        menubar.add_cascade(label="View")
        menubar.add_cascade(label="Help")
        master.config(menu=menubar)

        # Setup panels
        self.setup_left_panel()
        self.setup_center_canvas()
        self.setup_right_panel()

        # Bind keys and set initial states
        master.bind("<Escape>", self.undo_last_action)
        master.bind("q", lambda e: self.set_mode('landmark'))
        master.bind("w", lambda e: self.set_mode('obb'))
        master.bind("a", self.prev_image)
        master.bind("d", self.next_image)
        master.bind_all("z", lambda e: self.rotate_current_obb(-math.radians(10)))
        master.bind_all("x", lambda e: self.rotate_current_obb(-math.radians(1)))
        master.bind_all("c", lambda e: self.rotate_current_obb(math.radians(1)))
        master.bind_all("v", lambda e: self.rotate_current_obb(math.radians(10)))

        # Variables for image handling
        self.image_files = []
        self.current_image_index = -1
        self.image = None
        self.photo_image = None
        self.image_id = None
        self.file_path = None
        self.annotations = []
        self.obb_list = []
        self.current_obb_index = None
        self.mode = None
        self.set_mode('landmark')

    def set_mode(self, mode):
        if mode != self.mode:
            self.save_annotation()  # Save the current annotations
            self.clear_annotations()  # Clear the canvas before changing modes
        self.mode = mode
        if mode == 'landmark':
            self.canvas.bind("<Button-1>", self.on_canvas_click)
        elif mode == 'obb':
            self.canvas.bind("<Button-1>", self.start_rect)
            self.canvas.bind("<B1-Motion>", self.draw_rect)
            self.canvas.bind("<ButtonRelease-1>", self.fix_rect)

    def setup_left_panel(self):
        control_panel = Frame(self.master, width=60, bg='lightgray')
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        control_panel.pack_propagate(0)

        icons = ['open.png', 'save.png', 'next.png', 'prev.png',"robjects.png","cancel.png","zoom-in.png","zoom-out.png","fit-window.png","fit-width.png"]
        for icon_name in icons:
            self.add_icon_button(control_panel, icon_name)

    def setup_center_canvas(self):
        self.canvas = tk.Canvas(self.master, width=800, height=600, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def setup_right_panel(self):
        self.file_list_label = tk.Label(self.master, text="File List", bg='lightgray')
        self.file_list_label.pack(side=tk.TOP, fill=tk.X)
        self.file_list_box = Listbox(self.master)
        self.file_list_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def add_icon_button(self, panel, icon_name):
        icon_path = os.path.join('icons', icon_name)
        icon_image = Image.open(icon_path).resize((35, 35))
        photo = ImageTk.PhotoImage(icon_image)
        button = Button(panel, image=photo, command=lambda cmd=icon_name.split('.')[0]: self.on_icon_click(cmd))
        button.image = photo  # Keep a reference
        button.pack(pady=2)

    def on_icon_click(self, command_name):
        actions = {
            'open': self.load_image_directory,
            'save': self.save_annotation,
            'next': self.next_image,
            'prev': self.prev_image
        }
        action = actions.get(command_name)
        if action:
            action()

    def load_image_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.image_files = glob.glob(os.path.join(directory, '*.png')) + glob.glob(os.path.join(directory, '*.jpg'))
            self.image_files.sort()  # Sort the files to maintain a consistent order
            if self.image_files:
                self.save_annotation()  # Save current annotations before switching images
                self.clear_annotations()  # Clear current annotations
                self.current_image_index = 0
                self.update_file_list()
                self.load_image()

    def update_file_list(self):
        self.file_list_box.delete(0, tk.END)
        for file in self.image_files:
            self.file_list_box.insert(tk.END, os.path.basename(file))

    def update_selection(self):
        self.file_list_box.selection_clear(0, tk.END)
        self.file_list_box.selection_set(self.current_image_index)
        self.file_list_box.see(self.current_image_index)

    def load_image(self):
        if self.image_files:
            if self.file_path:  # Save annotations before loading new image
                self.save_annotation()
            self.file_path = self.image_files[self.current_image_index]
            self.image = Image.open(self.file_path)
            self.photo_image = ImageTk.PhotoImage(self.image)
            if self.image_id:
                self.canvas.delete(self.image_id)
            self.image_id = self.canvas.create_image(400, 300, image=self.photo_image, anchor=tk.CENTER)  # Center the image
            self.update_selection()
            self.clear_annotations()

    def next_image(self, event=None):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_image()

    def prev_image(self, event=None):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_image()

    def activate_landmark_mode(self, event):
        if self.mode != "landmark":
            self.save_annotation()
            self.mode = "landmark"
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            self.clear_annotations()

    def activate_obb_mode(self, event):
        if self.mode != "obb":
            self.save_annotation()
            self.mode = "obb"
            self.canvas.bind("<Button-1>", self.start_rect)
            self.canvas.bind("<B1-Motion>", self.draw_rect)
            self.canvas.bind("<ButtonRelease-1>", self.fix_rect)
            self.clear_annotations()

    def on_canvas_click(self, event):
        if self.mode == "landmark":
            if self.point is None:
                self.point = (event.x, event.y)
                self.point_id = self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill='blue')
            else:
                # 绘制线并计算角度
                line_id = self.canvas.create_line(self.point[0], self.point[1], event.x, event.y, fill='red', width=2)
                angle = math.atan2(event.y - self.point[1], event.x - self.point[0])  # 直接使用 atan2 计算角度
                self.lines.append((event.x, event.y, angle, line_id))  # 保存弧度，不转换为度
                if len(self.lines) == 2:
                    self.annotations.append((self.point, self.lines.copy()))
                    self.point = None
                    self.lines.clear()

    def start_rect(self, event):
        self.current_obb_index = len(self.obb_list)
        obb = {'start_point': (event.x, event.y), 'rect_id': [], 'angle': 0, 'cx': event.x, 'cy': event.y, 'w': 0, 'h': 0}
        rect_id = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='green', width=2)
        obb['rect_id'].append(rect_id)
        self.obb_list.append(obb)

    def draw_rect(self, event):
        if self.current_obb_index is not None:
            obb = self.obb_list[self.current_obb_index]
            self.canvas.coords(obb['rect_id'][0], obb['start_point'][0], obb['start_point'][1], event.x, event.y)

    def fix_rect(self, event):
        if self.current_obb_index is not None:
            obb = self.obb_list[self.current_obb_index]
            x0, y0 = obb['start_point']
            x1, y1 = event.x, event.y
            obb['cx'], obb['cy'] = (x0 + x1) / 2, (y0 + y1) / 2
            obb['w'], obb['h'] = abs(x1 - x0), abs(y1 - y0)
            self.redraw_obb(self.current_obb_index)

    def rotate_current_obb(self, delta_angle):
        if self.current_obb_index is not None and self.mode == "obb":
            obb = self.obb_list[self.current_obb_index]
            obb['angle'] += delta_angle
            obb['angle'] %= (2 * math.pi)
            self.redraw_obb(self.current_obb_index)

    def redraw_obb(self, index):
        obb = self.obb_list[index]
        self.canvas.delete(obb['rect_id'][0])
        angle_rad = obb['angle']
        cx, cy, w, h = obb['cx'], obb['cy'], obb['w'], obb['h']
        corners = [(cx + math.cos(angle_rad) * dx - math.sin(angle_rad) * dy,
                    cy + math.sin(angle_rad) * dx + math.cos(angle_rad) * dy)
                   for dx, dy in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]]
        new_id = self.canvas.create_polygon(*sum(corners, ()), outline='green', fill='', width=2)
        obb['rect_id'][0] = new_id  # Update ID with new polygon

    def save_annotation(self):
        if not (self.annotations or self.obb_list):  # Check if there is anything to save
            return  # Optionally, log this event or notify the user in another non-intrusive way

        # Determine the file suffix based on the current mode
        # suffix = "_landmark" if self.mode == "landmark" else "_obb"
        suffix = "" if self.mode == "landmark" else "_obb"
        filename = os.path.splitext(os.path.basename(self.file_path))[0] + suffix + ".xml"
        save_path = os.path.join(os.path.dirname(self.file_path), filename)
        folder = os.path.dirname(self.file_path)
        root = ET.Element("annotation")
        ET.SubElement(root, "folder").text = "Positive"
        ET.SubElement(root, "filename").text = os.path.basename(self.file_path).split('.')[0]
        ET.SubElement(root, "format").text = os.path.basename(self.file_path).split('.')[-1]
        source = ET.SubElement(root, "source")
        ET.SubElement(source, "database").text = "SWIM"
        size = ET.SubElement(root, "size")
        ET.SubElement(size, "width").text = str(self.image.width)
        ET.SubElement(size, "height").text = str(self.image.height)
        ET.SubElement(size, "depth").text = str(3 if self.image.mode == "RGB" else 1)  # Assumes images are either RGB or grayscale
        ET.SubElement(root, "segmented").text = "0"

        for annotation in self.annotations:
            point, lines = annotation
            obj = ET.SubElement(root, "object")
            ET.SubElement(obj, "type").text = "pointtheta"
            ET.SubElement(obj, "name").text = "wake"
            ET.SubElement(obj, "pose").text = "Unspecified"
            ET.SubElement(obj, "truncated").text = "0"
            ET.SubElement(obj, "difficult").text = "0"
            pointtag = ET.SubElement(obj, "pointtheta")
            ET.SubElement(pointtag, "px").text = f"{point[0]:.6f}"
            ET.SubElement(pointtag, "py").text = f"{point[1]:.6f}"
            ET.SubElement(pointtag, "theta1").text = f"{lines[0][2]:.2f}"
            ET.SubElement(pointtag, "theta2").text = f"{lines[1][2]:.2f}"



        for obb in self.obb_list:
            obj = ET.SubElement(root, "object")
            ET.SubElement(obj, "type").text = "robndbox"
            ET.SubElement(obj, "name").text = "wake"
            ET.SubElement(obj, "pose").text = "Unspecified"
            ET.SubElement(obj, "truncated").text = "0"
            ET.SubElement(obj, "difficult").text = "0"
            bbox = ET.SubElement(obj, "robndbox")
            ET.SubElement(bbox, "cx").text = str(obb['cx'])
            ET.SubElement(bbox, "cy").text = str(obb['cy'])
            ET.SubElement(bbox, "w").text = str(obb['w'])
            ET.SubElement(bbox, "h").text = str(obb['h'])

            # Normalize angle to be between 0 and π radians
            normalized_angle = obb['angle'] % (2 * math.pi)  # Normalize to 0-2π range first
            if normalized_angle > math.pi:
                normalized_angle = 2 * math.pi - normalized_angle  # Adjust to range 0-π

            ET.SubElement(bbox, "angle").text = f"{normalized_angle:.6f}"

        tree = ET.ElementTree(root)
        tree.write(save_path)

    def clear_annotations(self, event=None):
        self.canvas.delete("all")
        self.obb_list = []
        self.annotations = []  # Clear both lists
        if self.photo_image:
            self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)
        self.point = None
        self.lines = []
        self.current_obb_index = None

    def undo_last_action(self, event):
        if self.mode == "landmark" and self.lines:
            _, _, _, line_id = self.lines.pop()
            self.canvas.delete(line_id)
        elif self.mode == "landmark" and self.annotations:
            point, lines = self.annotations.pop()
            self.canvas.delete(self.point_id)
            for _, _, _, line_id in lines:
                self.canvas.delete(line_id)
            self.point = point[0], point[1]
            self.point_id = self.canvas.create_oval(self.point[0] - 5, self.point[1] - 5, self.point[0] + 5, self.point[1] + 5, fill='blue')
        elif self.mode == "obb" and self.current_obb_index is not None:
            obb = self.obb_list.pop(self.current_obb_index)
            for id in obb['rect_id']:
                self.canvas.delete(id)
            self.current_obb_index = None if not self.obb_list else 0  # Reset to first obb or None

def main():
    root = tk.Tk()
    app = ImageAnnotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()