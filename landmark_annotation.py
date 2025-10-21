import xml.etree.ElementTree as ET
import math
import os
def add_landmark(canvas, annotations, x, y):
    if not annotations['point']:
        annotations['point'] = (x, y)
        annotations['point_id'] = canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='blue')
    elif len(annotations['lines']) < 2:
        x0, y0 = annotations['point']
        line_id = canvas.create_line(x0, y0, x, y, fill='green', width=2)
        angle = math.degrees(math.atan2(y - y0, x - x0))
        if angle > 90:
            angle -= 180
        elif angle < -90:
            angle += 180
        annotations['lines'].append((x, y, angle, line_id))
        if len(annotations['lines']) == 2:
            annotations['full_annotation'].append((annotations['point'], annotations['lines']))
            annotations['point'] = None
            annotations['lines'] = []

def save_landmarks(annotations, file_path, image):
    root = ET.Element("annotation")
    filename = os.path.basename(file_path)
    ET.SubElement(root, "folder").text = "Positive"
    ET.SubElement(root, "filename").text = filename.split('.')[0]
    ET.SubElement(root, "format").text = filename.split('.')[-1]
    source = ET.SubElement(root, "source")
    ET.SubElement(source, "database").text = "SWIM"
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(image.width)
    ET.SubElement(size, "height").text = str(image.height)
    ET.SubElement(size, "depth").text = "3"
    ET.SubElement(root, "segmented").text = "0"
    for point, lines in annotations['full_annotation']:
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "type").text = "pointtheta"
        ET.SubElement(obj, "name").text = "wake"
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = "0"
        ET.SubElement(obj, "difficult").text = "0"
        pt = ET.SubElement(obj, "pointtheta")
        ET.SubElement(pt, "px").text = f"{point[0]:.6f}"
        ET.SubElement(pt, "py").text = f"{point[1]:.6f}"
        ET.SubElement(pt, "theta1").text = f"{lines[0][2]:.6f}"
        ET.SubElement(pt, "theta2").text = f"{lines[1][2]:.6f}"

    tree = ET.ElementTree(root)
    tree.write(file_path.replace(".jpg", "_annotations.xml"))
