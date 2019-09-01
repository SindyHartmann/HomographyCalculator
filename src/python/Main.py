from tkinter import *
import numpy as np
import decimal
from FieldWindow import FieldWindow

root = Tk()
app = FieldWindow(root)
root.mainloop()

print()
H = app.get_H()
print("H:")
print(H)
print()
image_points = app.get_image_points()
print("image_points:")
print(image_points)
print()
field_points = app.get_field_points()
print("field_points:")
print(field_points)
print()
for i in range(0,4):
    p3d = np.matrix([image_points[i][0],image_points[i][1],1])
    field_point = np.dot(np.linalg.inv(H),p3d.transpose())
    field_point = np.array(field_point/field_point[2],dtype=np.dtype(decimal.Decimal))
    print("first image_point as field_point: (x*H)")
    print(field_point)
print()