### HomographyCalculator

## Requirements and installation
* python 3
* pip
-> '$ pip install -r requirements.txt'

## use
Programm:
'$ python src/python/Main.py

use in other Programs:
use Class 'FieldWindow' as Window:
'root = Tk()
app = FieldWindow(root)
root.mainloop()'
You can get the homography matrix with 'app.get_H()'
and the picked points of the image and the game field with 
'app.get_image_points()' and
'app.get_field_points()' 
(see in src/python/Main.py)