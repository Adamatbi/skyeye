import osmnx as ox
from shapely.geometry import Polygon
from Plane import *
import math

class BaseMap:
    def __init__(self, polygon: Polygon) -> None:
        self.polygon = polygon
        self.features = ox.features_from_polygon(polygon, {'building': True})
        self.__points = None

    @property
    def points(self) -> list:
        if self.__points is not None:
            return self.__points
        self.__points = list(self.features['geometry'].apply(self.__extract_centre_of_polygon))
        return self.__points
    
    @property
    def corners(self) -> list:
        xx, yy = self.polygon.exterior.coords.xy
        x = list(xx)
        y = list(yy)
        return list(zip(y, x))
    
    def __extract_centre_of_polygon(self, polygon: Polygon) -> tuple[float, float]:
        minx, miny, maxx, maxy = polygon.bounds

        # Calculate the center point
        center_x = (minx + maxx) / 2
        center_y = (miny + maxy) / 2

        return (center_y,center_x)
    
    def plot(self, markersize:int=1) -> plt.plot:
        plot = plt.plot([x[0] for x in self.points],[x[1] for x in self.points], 'ro', markersize=markersize)
        return plot

    def get_plane(self) -> Plane:
        building_offsets = []
        origin_lon, origin_lat, far_corner_lon, far_corner_lat = self.polygon.bounds
        size = self.__calculate_offset_in_meters(origin_lat, origin_lon, far_corner_lat, far_corner_lon)
        reference_corner = self.corners[3]
        for building_coord in self.points:
            building_offsets.append(self.__calculate_offset_in_meters(reference_corner[0], reference_corner[1], building_coord[0], building_coord[1]))
        return Plane(building_offsets, size)
    
    def calculate_coordinates_from_offset(self, offset: tuple[float, float]) -> tuple[float, float]:
        lon, lat, _,_ = self.polygon.bounds
        earth_radius = 6371000
    
        # Convert distance from meters to degrees
        delta_lat = offset[1] / 111000
        
        # Convert longitude considering latitude
        delta_lon = offset[0] / (111000 * math.cos(math.radians(lat)))
        
        # New latitude and longitude
        new_lat = lat + delta_lat
        new_lon = lon + delta_lon
        
        return (new_lat, new_lon)
    

    def __calculate_offset_in_meters(self,lat1, lon1, lat2, lon2):
        # Calculate distance in meters using haversine formula
        distance = self.__haversine(lat1, lon1, lat2, lon2)
        
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
    
    def __haversine(self,lat1, lon1, lat2, lon2):
        # Radius of the Earth in meters
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

        # Distance between the two points
        distance = R * c
        return distance
    

class BaseMapGenerator:
    def __init__(self) -> None:
        pass

    def create_basemap_from_two_coords(self, coords: tuple[tuple[float,float], tuple[float,float]]) -> BaseMap:
        """
        Load buildings contained within square defined by two coordinates in decimal format. 
        The first tuple is top left, second is bottom right.
        """
        # calculate the edge points of the rectangle
        coordinates = [
            (coords[0][1], coords[0][0]),
            (coords[1][1], coords[0][0]),
            (coords[1][1], coords[1][0]),
            (coords[0][1], coords[1][0]),
            (coords[0][1], coords[0][0])
        ]

        # create polygon and query features
        polygon = Polygon(coordinates)
        basemap = BaseMap(polygon)
        return basemap

    def create_basemap_from_polygon(self, polygon: Polygon) -> BaseMap:
        """
        Load buildings contained within area defined by polygon
        """
        basemap = BaseMap(polygon)
        return basemap