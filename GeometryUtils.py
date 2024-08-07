import math
from shapely.geometry import Polygon

def calculate_point_angle(rotation_axis: tuple , point1: tuple, point2: tuple) -> float:
        """calculates the angle between two points with respect to a third point"""
        vector1 = (point1[0] - rotation_axis[0], point1[1] - rotation_axis[1])
        vector2 = (point2[0] - rotation_axis[0], point2[1] - rotation_axis[1])
        
        angle_vector1 = math.atan2(vector1[1], vector1[0])
        angle_vector2 = math.atan2(vector2[1], vector2[0])

        angle = math.degrees(angle_vector2 - angle_vector1)
        angle = (angle + 360) % 360
        
        return angle

def scale_points(points: list[tuple[float, float]], scale: float) -> list[tuple[float, float]]:
    """scales a set of points by a given factor"""
    scaled_points = [(x[0]*scale, x[1]*scale) for x in points]
    return scaled_points

def translate_points(points: list[tuple[float, float]], x: float, y: float) -> list[tuple[float,float]]:
    """translates a set of points by a given amount"""
    translated_points = [(pos[0]+x, pos[1]+y) for pos in points]
    return translated_points
                                                                                          

def rotate_points(points: list[tuple[float, float]], angle: float, rotation_axis: tuple[float,float]) -> list[tuple[float,float]]:
    """rotates a set of points by a given angle"""
    theta = math.radians(-angle)
    # translate to origin, rotate and translate back
    points = [(pos[0]-rotation_axis[0], pos[1]-rotation_axis[1]) for pos in points]
    points = [(pos[0]*math.cos(theta) - pos[1]*math.sin(theta), pos[0]*math.sin(theta) + pos[1]*math.cos(theta)) for pos in points]
    points = [(pos[0]+rotation_axis[0], pos[1]+rotation_axis[1]) for pos in points]
    return points


def extract_centre_of_polygon(polygon: Polygon) -> tuple[float, float]:
        minx, miny, maxx, maxy = polygon.bounds

        center_x = (minx + maxx) / 2
        center_y = (miny + maxy) / 2

        return (center_y,center_x)

def calculate_coordinates_from_offset(lat: float, lon: float, offset_east:float, offset_north:float) -> tuple[float, float]:
        # Convert distance from meters to degrees
        delta_lat = offset_north / 111000
        
        # Convert longitude considering latitude
        delta_lon = offset_east / (111000 * math.cos(math.radians(lat)))
        
        # New latitude and longitude
        new_lat = lat + delta_lat
        new_lon = lon + delta_lon
        
        return (new_lat, new_lon) 

def calculate_euclidean_distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
    """calculates the euclidean distance between two points"""
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def calculate_north_east_offset(lat1, lon1, lat2, lon2):
        # Calculate distance in meters using haversine formula
        distance = haversine(lat1, lon1, lat2, lon2)
        
        # Calculate bearing
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lambda = math.radians(lon2 - lon1)
        
        y = math.sin(delta_lambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - \
            math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
        bearing = math.atan2(y, x)
        
        # Calculate north and east components
        distance_north = distance * math.cos(bearing)
        distance_east = distance * math.sin(bearing)
    
        return distance_east,distance_north    

def haversine(lat1, lon1, lat2, lon2):
        R = 6371000

        # Convert latitude and longitude from degrees to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        # Haversine formula
        a = math.sin(delta_phi / 2.0)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance
    