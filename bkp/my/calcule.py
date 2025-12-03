# erstelle eine klasse die koordinaten in einem 3d raum speichert
# ruckgaben multiple values from a function in einem array und ein punkt in der zeit weist aud die cordinaten des objekts dar

class Cords:
    def __init__(self):
        self.time_points = []

    def save_new_point(self, x, y, z, t):
        for point in self.time_points:
            if point[3] == t:
                return
        self.time_points.append((x, y, z, t))
    
    def get_point_at_time(self, t):
        for point in self.time_points:
            if point[3] == t:
                return point
            
    def get_all_points(self):
        return self.time_points
    
    def clear_points(self):
        self.time_points = []
    
    # def update_point(self, x, y, z, t):



if __name__ == "__main__":
    print("Hello, World!")
    # points = Cords()
    ## test how many ram the points use for 1 million points

    import sys 
    import time

    f = {}

    start_ram = sys.getsizeof(f)
    start_time = time.time()

    for i in range(1000000):
        # points.save_new_point(i+2, i+1.2, i+1.5, i+1)
        f[i] = (i+2, i+1.2, i+1.5)
        print(i)
        
    end_ram = sys.getsizeof(f)
    end_time = time.time()

    print(f"Used RAM for 1 million points: {end_ram - start_ram} bytes")
    print(f"Time taken to save 1 million points: {end_time - start_time} seconds")

    # print(points.get_point_at_time(3))