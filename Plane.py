from matplotlib import pyplot as plt
import math
import numpy as np
from scipy.spatial import KDTree

class Plane:
    def __init__(self, points: list[tuple[float, float]],size:tuple[float,float]) -> None:
        self.base_points = points
        self.size = size
        self.corners = [(0,0), (size[0],0), (size[0],size[1]), (0,size[1])]
        self.__scale = 1
        self.__translation = (0,0)
        self.__rotation = 0

    def plot(self, markersize:int=1) -> plt.plot:
        plot = plt.plot([x[0] for x in self.transformed_points],[x[1] for x in self.transformed_points], 'ro', markersize=markersize)
        return plot

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
    def transformed_points(self) -> list[tuple[float, float]]:
        manipulated_points = self.__apply_transformations(self.base_points)
        return manipulated_points
    
    @property
    def transformed_centre(self) -> tuple[float, float]:
        transformed_centre = self.__apply_transformations([(self.size[0]/2, self.size[1]/2)])
        return transformed_centre[0]
    
    @property
    def num_points(self) -> int:
        return len(self.base_points)
    

class Fingerprint:
    def __init__(self, distance_ratios: list[float], angles: list[float]) -> None:
        self.datapoints = list(zip(distance_ratios, angles))
        self.distance_ratios = distance_ratios
        self.angles = angles
        

class PlaneComparitor:
    def __init__(self) -> None:
        pass

    def measure_offsets(self, plane1: Plane, plane2: Plane, outlier_threshold: float = 0.95) -> float:
        transformed_points1 = plane1.transformed_points
        tree = KDTree(plane2.transformed_points)
        distances, _ = tree.query(transformed_points1)
        return distances
    
    def discard_outliers(self, distances: list[float], threshold: float) -> list[float]:
        if threshold < 0 or threshold > 1:
            raise ValueError("Threshold must be between 0 and 1")
        distances.sort()
        return distances[:int(len(distances)*threshold)]

    def create_fingerprints(self, plane:Plane, num_samples:int) -> list:
        """returns a unique fingerprint for each point in the plane"""
        transformed_points = plane.transformed_points
        tree = KDTree(plane.transformed_points)
        fingerprints = []
        for i in range(plane.num_points):
            distances, indexes = tree.query(transformed_points[i],k=num_samples+2)
            distance_ratios = (distances/distances[1])[2:]
            angles = [self.__calculate_angle(transformed_points[i], transformed_points[indexes[1]], transformed_points[j]) for j in indexes[2:]]
            fingerprints.append(Fingerprint(distance_ratios,angles))
        return fingerprints            
    
    def compare_fingerprint(self, base_fingerprint: Fingerprint, overlay_fingerprint: Fingerprint, num_drop:int) -> float:
        """loss is calculated as the sum of the product of the angle and distance differences between the closest points.
        the worst N losses are dropped before summing"""
        losses = []
        for overlay_distance_ratio, overlay_angle in overlay_fingerprint.datapoints:
            min_loss = float('inf')
            for base_distance_ratio, base_angle in base_fingerprint.datapoints:
                angle_difference = abs(overlay_angle - base_angle)
                distance_difference = abs(overlay_distance_ratio - base_distance_ratio)
                loss = angle_difference * distance_difference
                if loss < min_loss:
                    min_loss = loss
            losses.append(min_loss)
        losses.sort()
        
        sum_loss = sum(losses[:-num_drop]) if num_drop>0 else sum(losses)
        return sum_loss
    
    def __calculate_angle(self, rotation_axis, point1, point2):
        vector1 = (point1[0] - rotation_axis[0], point1[1] - rotation_axis[1])
        vector2 = (point2[0] - rotation_axis[0], point2[1] - rotation_axis[1])
        
        angle_vector1 = math.atan2(vector1[1], vector1[0])
        angle_vector2 = math.atan2(vector2[1], vector2[0])

        angle = math.degrees(angle_vector2 - angle_vector1)
        angle = (angle + 360) % 360
        
        return angle
    
class LocationResolver:
    def __init__(self) -> None:
        pass
