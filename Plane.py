from matplotlib import pyplot as plt
import math
import numpy as np

class Plane:
    def __init__(self, points: list[tuple[float, float]],size:tuple[float,float]) -> None:
        self.base_points = points
        self.__manipulated_points = points
        self.size = size
        self.corners = [(0,0), (size[0],0), (size[0],size[1]), (0,size[1])]
        self.__scale = 1
        self.__translation = (0,0)
        self.__rotation = 0

    def plot(self, markersize:int=1) -> plt.plot:
        plot = plt.plot([x[0] for x in self.points],[x[1] for x in self.points], 'ro', markersize=markersize)
        return plot
    
    def reset_manipulated_points(self) -> None:
        self.__manipulated_points = self.base_points

    def set_scale(self, scale: float) -> None:
        self.__scale = scale

    def set_translation(self, x: float, y: float) -> None:
        self.__translation = (x,y)

    def set_rotation(self, angle: float) -> None:
        self.__rotation = angle

    def __apply_transformations(self, points: list) -> None:
        if self.__rotation!=0:
            theta = np.radians(-self.__rotation)
            # translate to origin, rotate and translate back
            points = [(pos[0]-self.size[0]/2, pos[1]-self.size[1]/2) for pos in points]
            points = [(pos[0]*math.cos(theta) - pos[1]*math.sin(theta), pos[0]*math.sin(theta) + pos[1]*math.cos(theta)) for pos in points]
            points = [(pos[0]+self.size[0]/2, pos[1]+self.size[1]/2) for pos in points]
        if self.__scale!=1:
            points = [(x[0]*self.__scale, x[1]*self.__scale) for x in points]
        if self.__translation!=(0,0):
            points = [(pos[0]+self.__translation[0], pos[1]+self.__translation[1]) for pos in points]
        return points
    
    @property
    def points(self) -> list[tuple[float, float]]:
        self.__manipulated_points = self.__apply_transformations(self.base_points)
        return self.__manipulated_points
    
    @property
    def transformed_centre(self) -> tuple[float, float]:
        transformed_centre = self.__apply_transformations([(self.size[0]/2, self.size[1]/2)])
        return transformed_centre[0]