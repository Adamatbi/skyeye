from ultralytics import YOLO
import cv2
import numpy as np
from matplotlib import pyplot as plt
from src.Plane import *

class VisionModel:
    def __init__(self, model_path: str) -> None:
        self.model = YOLO(model_path)

    def run_inference(self, image_path: str, conf: int=0.9) -> np.ndarray:
        img = cv2.imread(image_path)
        results = self.model.predict(source=img, conf=conf, save=False, verbose=False)
        return VisionModelResult(results, image_path)
    
    
class VisionModelResult:
    def __init__(self, results: np.ndarray, image_path:str) -> None:
        self.__results = results
        self.__image_path = image_path
        self.__point_locations = None
    
    def display_dots(self, color:tuple=(0,0,255), radius: int = 5,thickness:int = 10) -> np.ndarray:
        boxes = self.__results[0].boxes.data.numpy() 
        image = cv2.imread(self.__image_path)
        for box in boxes:
            centre_coordinates = (int((box[0] + box[2])/2), int((box[1] + box[3])/2))
            cv2.circle(image, centre_coordinates, radius, color, thickness)
        return image
        
    def display_boxes(self, color:tuple=(0,0,255), thickness:int = 5) -> np.ndarray:
        boxes = self.__results[0].boxes.data.numpy()
        image = cv2.imread(self.__image_path)
        for box in boxes:
            start_point = (int(box[0]), int(box[1])) 
            end_point = (int(box[2]), int(box[3])) 
            cv2.rectangle(image, start_point, end_point, color, thickness) 
        return image
    
    def plot(self, markersize:int=1) -> plt.plot:
        plot = plt.plot([x[0] for x in self.points],[x[1] for x in self.points], 'ro', markersize=markersize)
        return plot
    
    def get_plane(self) -> list:
        return Plane(self.points,( self.image_resolution[1], self.image_resolution[0]))
    
    @property
    def points(self) -> np.ndarray:
        if self.__point_locations is not None:
            return self.__point_locations
        boxes = self.__results[0].boxes.data.numpy() 
        image_height = self.__results[0].orig_shape[0]
        self.__point_locations = []
        for box in boxes:
            centre_coordinates = (int((box[0] + box[2])/2), image_height-int((box[1] + box[3])/2))
            self.__point_locations.append(centre_coordinates)

        return self.__point_locations
    
    @property
    def image_resolution(self) -> tuple:
        return self.__results[0].orig_shape