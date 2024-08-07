import osmnx as ox
from shapely.geometry import Polygon
from GeometryUtils import *
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
        self.__points = list(self.features['geometry'].apply(extract_centre_of_polygon))
        return self.__points
    
    @property
    def corners(self) -> list:
        xx, yy = self.polygon.exterior.coords.xy
        x = list(xx)
        y = list(yy)
        return list(zip(y, x))
    
    def plot(self, markersize:int=1) -> plt.plot:
        plot = plt.plot([x[0] for x in self.points],[x[1] for x in self.points], 'ro', markersize=markersize)
        return plot

    def get_plane(self) -> Plane:
        building_offsets = []
        origin_lon, origin_lat, far_corner_lon, far_corner_lat = self.polygon.bounds
        size = calculate_north_east_offset(origin_lat, origin_lon, far_corner_lat, far_corner_lon)
        reference_corner = self.corners[3]
        for building_coord in self.points:
            building_offsets.append(calculate_north_east_offset(reference_corner[0], reference_corner[1], building_coord[0], building_coord[1]))
        return Plane(building_offsets, size)

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