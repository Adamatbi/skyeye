import geopandas as gpd
import osmnx as ox
from shapely.geometry import Polygon

class BaseMap:
    def __init__(self, polygon: Polygon) -> None:
        self.polygon = polygon
        self.features = ox.features_from_polygon(polygon, {'building': True})
        self.points = None

    def get_points(self) -> list:
        if self.points is not None:
            return self.points
        self.points = list(self.features['geometry'].apply(self.__extract_centre_of_polygon))
        return self.points
    
    def get_corners(self) -> list:
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