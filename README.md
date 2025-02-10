# Plane-Sweep 


Dependencies:
1. bintrees
2. matplotlib

In order to run this program, you have to install bintrees and matplotlib libraries using 
    "pip install bintrees matplotlib" 
as this libraries helps us implement a balanced Red black balanced binary tree and the plots for the visualization respectively.

The algorithm assume that the line segments are in general position: 
1.  x-coordinates and y-coordinates of endpoints and intersection points are distinct. 
    • This implies that no line segment is vertical or horizonal. 
2.  If two segments intersect, then they intersect in a single point. 
    • There are no collinear lines. 
3.  No three line segments intersect in a common point.
4. No end point lies on another segment


If the segments provided do not obey these rules, the program might not run as expected


There are two files in this folder. plane_sweep.py and segments.txt. The program file is written in python. The program file accepts a list of line segments and returns a txt file containing the intersection points within those line segments. The other file is a sample txt file that describes how the segments are to be represented. 

You can run either program with the command
python <program_name> <file_path>
    e.g python plane_sweep.py ./segments.txt

You can copy the points into the points.txt file if you want to run the program with the ./segments.txt file path or you can include a file path to your own points. 


Output for each program is going to be created after the program is run with the name intersections.txt. The first line in the output is the number of intersection points. Every other line represent the points.





