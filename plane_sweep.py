import sys
from bintrees import RBTree
from functools import total_ordering


sweep_line = 1
is_start = False
# Create point class, line segment class
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        # Compare points by x, then by y
        return (self.y, self.x) < (other.y, other.x)
    
    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
@total_ordering
class LineSegment:
    def __init__(self, p1, p2):
        self.p1 = min(p1, p2)  # Always make p1 the leftmost point
        self.p2 = max(p1, p2)
        self.priority = Point(0, 0)
       

    def updatePriority(self):
        # Calculate the y-coordinate of the intersection with the sweep line using the equation of the line formula y = mx + c
        y_intersection = ((self.p2.y - self.p1.y) / (self.p2.x - self.p1.x)) * (sweep_line - self.p1.x) + self.p1.y
        intersection_pt = Point(sweep_line, y_intersection) 
        # assign the intersection point as the priority of the segment. this allows the segments in the active segments tree to be ordered by priority 
        return intersection_pt
    
    def __lt__(self, other):
        global is_start
        # Compare segments by priority
        if is_start:
            self.priority = self.updatePriority()
            other.priority = other.updatePriority()
        return self.priority < other.priority
    def __repr__(self):
        return f"LineSegment({self.p1}, {self.p2})"

    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2
    
# Helper to determine if two line segments intersect. In order to see if two lines intersect, we need to find the cross product of both the endpoints w.r.t the other line segment and ensure that they are not equal. If colinearity occurs, handle special cases
def cross_product(p, q, r):
    cp = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if cp == 0:
        return 0  # Collinear
    elif cp > 0:
        return 1  # Clockwise
    else:
        return 2  # Counterclockwise
# Helper to find if point lies on a segment
def on_segment(p, q, r):
    return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))

def segments_intersect(seg1, seg2):
    """Checks if two line segments intersect."""
    p1, q1 = seg1.p1, seg1.p2
    p2, q2 = seg2.p1, seg2.p2

    # Find the 4 orientations required for general and special cases
    o1 = cross_product(p1, q1, p2)
    o2 = cross_product(p1, q1, q2)
    o3 = cross_product(p2, q2, p1)
    o4 = cross_product(p2, q2, q1)

    # General case
    if o1 != o2 and o3 != o4:
        return True
    
    # Special Cases
    # p1, q1 and p2 are collinear and p2 lies on segment p1q1
    if o1 == 0 and on_segment(p1, p2, q1):
        return True

    # p1, q1 and q2 are collinear and q2 lies on segment p1q1
    if o2 == 0 and on_segment(p1, q2, q1):
        return True

    # p2, q2 and p1 are collinear and p1 lies on segment p2q2
    if o3 == 0 and on_segment(p2, p1, q2):
        return True

    # p2, q2 and q1 are collinear and q1 lies on segment p2q2
    if o4 == 0 and on_segment(p2, q1, q2): 
        return True

    return False

# Helper for finding out intersection point
def line_equation(seg):
    p1, p2 = seg.p1, seg.p2
    A = p2.y - p1.y
    B = p1.x - p2.x
    C = p2.x * p1.y - p1.x * p2.y
    return A, B, C

# Calculate intersection point using Cramer's rule for a system of linear equations. 
def calculate_intersection_point(seg1, seg2):
    A1, B1, C1 = line_equation(seg1)
    A2, B2, C2 = line_equation(seg2)
    
    determinant = A1 * B2 - A2 * B1
    
    x = (B1 * C2 - B2 * C1) / determinant
    y = (A2 * C1 - A1 * C2) / determinant
    
    return Point(x, y)

# Event class to represent events in the queue
class Event:
    def __init__(self, point, segment, event_type):
        self.point = point
        self.segment = segment
        self.event_type = event_type  # start, end, intersection

    def __lt__(self, other):
        # Events are ordered by point x-coordinate, then y-coordinate
        return self.point < other.point

    def __repr__(self):
        return f"Event({self.point}, {self.event_type})"
    

def plane_sweep(segments):
    global sweep_line
    global is_start
    intersections = set()
    count = 0
    event_queue = RBTree()  # Event queue using RBTree
       
    # Look at segment above for intersection
    def check_above(seg, active_segments, event_queue):
        try:
            above_seg = active_segments.prev_item(seg)[0]
            if segments_intersect(seg, above_seg):
                intersection_point = calculate_intersection_point(seg, above_seg) 
                if intersection_point.x >= sweep_line: 
                    print(f"Intersection at {intersection_point} between {seg} and {above_seg}")
                    new_event = Event(intersection_point, (above_seg, seg), "intersection")
                    intersections.add((intersection_point.x, intersection_point.y))
                    event_queue.insert(new_event.point, new_event)
        except KeyError:
            pass
    # Look at segment below for intersection
    def check_below(seg, active_segments, event_queue):
        try:
            below_seg = active_segments.succ_item(seg)[0]
            if segments_intersect(seg, below_seg):
                intersection_point = calculate_intersection_point(seg, below_seg) 
                if intersection_point.x >= sweep_line:
                    print(f"Intersection at {intersection_point} between {seg} and {below_seg}")
                    new_event = Event(intersection_point, (seg, below_seg), "intersection")
                    intersections.add((intersection_point.x, intersection_point.y))
                    event_queue.insert(new_event.point, new_event)
        except KeyError:
            pass
    # Step 1: Initialize the event queue with the start and end points of all segments
    for seg in segments:
        start_event = Event(seg.p1, seg, "start")  # Start of segment
        end_event = Event(seg.p2, seg, "end")    # End of segment
        event_queue.insert(start_event.point, start_event)
        event_queue.insert(end_event.point, end_event)
        
    active_segments = RBTree()  # Active segments maintained in a balanced BST

    # Step 2: Process each event in the queue
    while event_queue:
        
        event = event_queue.pop_min()[1]
        sweep_line = event.point.x
        point = event.point
        seg = event.segment
        
        if event.event_type == "start":  # Start of segment
            is_start = True
            print(f"Start of {seg} at {point}")

            # insert new segment to active_segments
            # get priority for new event segment
            # y_intersection = ((starting_segment.p2.y - starting_segment.p1.y) / (starting_segment.p2.x - starting_segment.p1.x)) * (sweep_line - starting_segment.p1.x) + starting_segment.p1.y
            # starting_segment.priority = Point(sweep_line, y_intersection)
            active_segments.insert(seg, seg)
            is_start = False
            # Check for intersections with the above neighbor (predecessor)
            check_above(seg, active_segments, event_queue)

            # Check for intersections with the below neighbor (successor)
            check_below(seg, active_segments, event_queue)
            
        elif event.event_type == "end":  # End of segment
            print(f"End of {seg} at {point}")
            global is_intersection
            is_intersection = True
            active_segments.remove(seg)  # Remove segment from active segments
            # check new neighbours for intersection
            try:
                above_seg = active_segments.prev_item(seg)[0]
                below_seg = active_segments.succ_item(seg)[0]
                if segments_intersect(above_seg, below_seg):
                    intersection_point = calculate_intersection_point(above_seg, below_seg)
                    if intersection_point.x >= sweep_line:
                        print(f"Intersection at {intersection_point} between {seg} and {above_seg}")
                        new_event = Event(intersection_point, (above_seg, seg), "intersection")
                        intersections.add((intersection_point.x, intersection_point.y))
                        event_queue.insert(new_event.point, new_event)
            except KeyError:
                pass
            is_intersection = False
        elif event.event_type == "intersection":  # Intersection event
            is_intersection = True
            print(f"Intersection event between {seg} at {point}")
            # Handle intersection logic if needed
            above_seg = event.segment[0]
            below_seg = event.segment[1]
            # if above_seg.p1 != event.point and below_seg.p1 != event.point:
            for item in active_segments:
                # print(item, item.priority)
                if (item == above_seg):
                    
                    above_seg = item
                elif item == below_seg:
                    
                    below_seg = item      
            print(active_segments)
            active_segments.remove(above_seg)  
            active_segments.remove(below_seg)    
            above_seg.priority, below_seg.priority = below_seg.priority, above_seg.priority
            active_segments.insert(above_seg, above_seg)
            active_segments.insert(below_seg, below_seg)
            check_below(above_seg, active_segments, event_queue)
            check_above(below_seg, active_segments, event_queue)

        
        # if count > 30:
        #     break
        count +=1 
    print("sweep_line: ", sweep_line)
    return intersections


def get_line_segments(file_path):
    segments = []
    with open(file_path, 'r') as file:
        # Discard number of segments
        file.readline()

        # Process each subsequent line
        for line in file:
            # Split line into x and y coordinates
            point1_x, point1_y, point2_x, point2_y = line.split()
            segments.append(LineSegment(
                Point((float(point1_x)), float(point1_y)), 
                Point(float(point2_x), float(point2_y))
            ))
    return segments



def main():
    if len(sys.argv) != 2:
        print("Please add a file path for the line segments. Usage: python plane_sweep.py <file_path>")
        return
    
    file_path = sys.argv[1]
    segments = get_line_segments(file_path)
    intersections = plane_sweep(segments)
    print("sweep_line: ", sweep_line)
    import matplotlib.pyplot as plt

    # Create the plot
    plt.figure(figsize=(12, 12))

    # Plot each line segment
    for i, segment in enumerate(segments, 1):
        x_coords = [segment.p1.x, segment.p2.x]
        y_coords = [segment.p1.y, segment.p2.y]
        plt.plot(x_coords, y_coords, color="blue")

        # Plot the endpoints
        plt.plot(segment.p1.x, segment.p1.y, 'o', markersize=4, color="green")
        plt.plot(segment.p2.x, segment.p2.y, 'o', markersize=4, color="green")

    # Plot intersection points
    for point in intersections:
        plt.plot(point[0], point[1], 'ro', markersize=2)  # 'ro' for red circle

    # Create legend elements
    blue_line = plt.Line2D([], [], color="blue", label="Segments")
    green_point = plt.Line2D([], [], color="green", marker='o', markersize=4, linestyle='None', label="Endpoints")
    red_point = plt.Line2D([], [], color="red", marker='o', markersize=2, linestyle='None', label="Intersections")

    # Add legend
    plt.legend(handles=[blue_line, green_point, red_point], loc='upper right')

    # Set labels and title
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Visualization of Line Segments')

    # Set equal aspect ratio
    plt.axis('equal')

    # Show grid
    plt.grid(True)

    # Show the plot
    plt.show()

    with open('intersections.txt', 'w') as file:
        # Write the number of intersections as the first line
        file.write(f"{len(intersections)}\n")
        # Loop through intersections
        for intersection in intersections:
            # Format and write each point to the file
            file.write(f"{intersection[0]} {intersection[1]}\n")

if __name__ == "__main__":
    main()
