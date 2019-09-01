from HomographyCalculation import HomographyCalculation
import numpy as np
import decimal

p1 = [[35,31],[35,16],[12,31],[12,16]]
p2 = [[0,0],[0,20],[20,0],[20,20]]

cal = HomographyCalculation(p1,p2)
cal.start_Calculation()
H = cal.get_H()

print(H)

print()
print(p1)
print(p2)
print()
for i in range(0,4):
    p3d = np.matrix([p1[i][0],p1[i][1],1])
    field_point = np.dot(H,p3d.transpose())
    field_point = np.array(field_point/field_point[2],dtype=np.dtype(decimal.Decimal))
    print("{}. image_point as 3d point: (H*x)".format(i+1))
    print(field_point)
    field_point = np.dot(field_point.transpose(),np.linalg.inv(H))
    field_point = np.array(field_point/field_point[0,2],dtype=np.dtype(decimal.Decimal))
    print("{}. image_point as field_point: (H*x)".format(i+1))
    print(field_point)