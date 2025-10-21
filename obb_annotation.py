import xml.etree.ElementTree as ET
import math
import os


# def start_obb(self, event):
#     """Start a new OBB when the user clicks on the canvas."""
#     x, y = event.x, event.y
#     self.current_obb = {
#         'rect_id': self.canvas.create_polygon(x, y, x, y, x, y, x, y, outline='red', width=2),
#         'start_point': (x, y),
#         'angle': 0  # Start with no rotation
#     }
#     print("New OBB started")

def create_obb(canvas, event, current_obb):
    # Initialize the polygon with the same start point for all four corners to form a degenerate rectangle initially.
    x, y = event.x, event.y
    rect_id = canvas.create_rectangle(x, y, x, y, x, y, x, y, outline='red', fill='', width=2)
    current_obb['rect_id'] = rect_id
    current_obb['start_point'] = (x, y)
    current_obb['angle'] = 0

def update_obb(self, event):
    """Update the current OBB's size as the mouse is dragged."""
    if 'rect_id' in self.current_obb:
        x0, y0 = self.current_obb['start_point']
        x1, y1 = event.x, event.y
        self.canvas.coords(self.current_obb['rect_id'],
                           x0, y0,  # Top-left
                           x1, y0,  # Top-right
                           x1, y1,  # Bottom-right
                           x0, y1)  # Bottom-left


def finalize_obb(canvas, current_obb, obb_list):
    """Finalize the OBB and add it to the list, check if 'rect_id' exists before proceeding."""
    if 'rect_id' in current_obb:
        x0, y0, x1, y1 = canvas.coords(current_obb['rect_id'])
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        w, h = abs(x1 - x0), abs(y1 - y0)
        current_obb.update({'cx': cx, 'cy': cy, 'w': w, 'h': h, 'angle': current_obb.get('angle', 0)})
        obb_list.append(current_obb.copy())
        current_obb.clear()
    else:
        print("No OBB to finalize")


import math

def rotate_obb(canvas, current_obb, delta_angle):
    """Rotate the selected OBB by a given angle in degrees."""
    if 'rect_id' in current_obb:
        # Convert delta angle from degrees to radians and update the current angle
        delta_rad = math.radians(delta_angle)
        current_obb['angle'] += delta_rad
        print(f"Updated angle in radians: {current_obb['angle']} (degrees: {math.degrees(current_obb['angle'])})")

        # Fetch the current coordinates of the OBB
        coords = canvas.coords(current_obb['rect_id'])
        if len(coords) != 8:
            print("Error: Incorrect number of coordinates for rotation.")
            return

        # Compute the geometric center of the OBB
        cx = (coords[0] + coords[2] + coords[4] + coords[6]) / 4
        cy = (coords[1] + coords[3] + coords[5] + coords[7]) / 4
        print(f"Center before rotation: ({cx}, {cy})")

        # Calculate new coordinates for each corner
        new_coords = []
        for i in range(0, len(coords), 2):
            dx, dy = coords[i] - cx, coords[i+1] - cy
            new_x = cx + (dx * math.cos(current_obb['angle']) - dy * math.sin(current_obb['angle']))
            new_y = cy + (dx * math.sin(current_obb['angle']) + dy * math.cos(current_obb['angle']))
            new_coords.extend([new_x, new_y])

        # Update the coordinates on the canvas
        canvas.coords(current_obb['rect_id'], new_coords)
        print(f"New coordinates: {new_coords}")


def rotate_selected_obb(canvas, current_obb, delta_angle):
    if 'rect_id' in current_obb:
        current_obb['angle'] += math.radians(delta_angle)  # Increment the angle in radians
        angle_rad = current_obb['angle']
        coords = canvas.coords(current_obb['rect_id'])
        if len(coords) != 8:
            print("Error: OBB polygon coordinates are not valid.")
            return

        cx, cy = (coords[0] + coords[4]) / 2, (coords[1] + coords[5]) / 2
        new_coords = []
        for i in range(0, len(coords), 2):
            dx, dy = coords[i] - cx, coords[i+1] - cy
            new_x = cx + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            new_y = cy + dy * math.cos(angle_rad) + dx * math.sin(angle_rad)
            new_coords.extend([new_x, new_y])

        canvas.coords(current_obb['rect_id'], new_coords)




def redraw_obb(canvas, current_obb):
    if 'rect_id' in current_obb:
        coords = canvas.coords(current_obb['rect_id'])
        if len(coords) != 8:
            print("Error: OBB polygon coordinates are not valid.")
            return
        # Calculate center, width, and height
        x0, y0, x1, y1 = coords[0], coords[1], coords[4], coords[5]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        w, h = abs(x1 - x0), abs(y1 - y0)
        angle_rad = current_obb['angle']

        # Calculate the new corners using the rotation angle
        corners = [
            (cx + math.cos(angle_rad) * dx - math.sin(angle_rad) * dy,
             cy + math.sin(angle_rad) * dx + math.cos(angle_rad) * dy)
            for dx, dy in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        ]
        # Flatten the list of corners and update the canvas coordinates
        flat_corners = [coord for point in corners for coord in point]
        canvas.coords(current_obb['rect_id'], flat_corners)



def save_obbs(obb_list, file_path, image):
    root = ET.Element("annotation")
    ET.SubElement(root, "folder").text = "Positive"
    ET.SubElement(root, "filename").text = os.path.splitext(os.path.basename(file_path))[0]
    ET.SubElement(root, "format").text = "jpg"
    source = ET.SubElement(root, "source")
    ET.SubElement(source, "database").text = "SWIM"
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(image.width)
    ET.SubElement(size, "height").text = str(image.height)
    ET.SubElement(size, "depth").text = "3"
    ET.SubElement(root, "segmented").text = "0"

    for obb in obb_list:
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "type").text = "robndbox"
        ET.SubElement(obj, "name").text = "wake"
        robndbox = ET.SubElement(obj, "robndbox")
        ET.SubElement(robndbox, "cx").text = str(obb['cx'])
        ET.SubElement(robndbox, "cy").text = str(obb['cy'])
        ET.SubElement(robndbox, "w").text = str(obb['w'])
        ET.SubElement(robndbox, "h").text = str(obb['h'])
        ET.SubElement(robndbox, "angle").text = str(math.degrees(obb['angle']))

    tree = ET.ElementTree(root)
    tree.write(file_path.replace(".jpg", "_obb.xml"))
