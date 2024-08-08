from Vision import *
from Map import *
import time
    
class LocationResolver:
    def __init__(self,vision_model_path:str) -> None:
        self.vision_model = VisionModel(vision_model_path)
        self.map_generator = BaseMapGenerator()
        self.comparitor = PlaneComparitor()


    def get_location(self, image_path:str,search_area: Polygon, drone_height_range:tuple[float,float], fingerprint_point_count: int = 7) -> dict:
        #create a plane from the image
        vision_result = self.vision_model.run_inference(image_path)
        photo_plane = vision_result.get_plane()

        #create a plane from the map
        basemap = self.map_generator.create_basemap_from_polygon(search_area)
        map_plane = basemap.get_plane()

        #create fingerprints for points in each plane
        photo_fingerprints = self.comparitor.create_fingerprints(photo_plane, fingerprint_point_count)
        map_fingerprints = self.comparitor.create_fingerprints(map_plane, fingerprint_point_count)

        #find matching points from the two planes with the closest fingerprints
        fingerprint_matches = self.comparitor.match_fingerprints(map_fingerprints,photo_fingerprints)

        photo_point_matches = [photo_plane.base_points[x] for x in fingerprint_matches["overlay_matches"]]
        map_point_matches = [map_plane.base_points[x] for x in fingerprint_matches["base_matches"]]

        match_comparisons = 15
        solution_fit = float("inf")

        # while the solution is above threshold, increase the number of comparisons
        while(solution_fit>6):
            possible_solutions = self.__find_possible_solutions(photo_plane, map_plane, photo_point_matches, map_point_matches, drone_height_range, match_comparisons)
            if len(possible_solutions)>0:
                solution_fit = possible_solutions[0][0]
            match_comparisons *= 2

        #apply the best solution to the photo plane
        photo_plane.set_rotation(possible_solutions[0][1])
        photo_plane.set_translation(possible_solutions[0][2][0], possible_solutions[0][2][1])
        photo_plane.set_scale(possible_solutions[0][3])

        #calculate the drone coordinates
        photo_centre = photo_plane.transformed_centre
        print(photo_centre)
        lat, lon = basemap.corners[3]
        drone_coords = calculate_coordinates_from_offset(lat,lon, photo_centre[0], photo_centre[1])
        drone_height = int(possible_solutions[0][4])
        
        return {"location":drone_coords, "height":drone_height} 

    def __find_possible_solutions(self, photo_plane: Plane, map_plane: Plane, photo_matches: list[tuple[float,float]], map_matches: list[tuple[float,float]], drone_height_range: tuple[float,float], testing_range:int = 20) -> list:
        """line up all combinations of two matching fingerprint points from the photo and map planes and check the quality of the solution"""
        possible_solutions = []
        for index1 in range(testing_range):
            for index2 in range(index1+1, testing_range):
                
                drone_height = self.__calculate_drone_height(map_plane, photo_plane,map_matches[index1], map_matches[index2], photo_matches[index1], photo_matches[index2])
                if drone_height<drone_height_range[0] or drone_height>drone_height_range[1]:
                    continue

                rotation, translation, scale = self.__calculate_transformations_from_2_points(map_matches[index1], map_matches[index2], photo_matches[index1], photo_matches[index2],photo_plane.size) 
                
                photo_plane.set_rotation(rotation)
                photo_plane.set_translation(translation[0], translation[1])
                photo_plane.set_scale(scale)

                #calculate solution quality
                distances = self.comparitor.measure_offsets(photo_plane, map_plane)
                distances = self.comparitor.discard_outliers(distances, 0.90)

                possible_solutions.append((sum(distances)/len(distances), rotation, translation, scale, drone_height))

        possible_solutions.sort(key=lambda x: x[0])
        return possible_solutions



    def __calculate_transformations_from_2_points(self, base_point1: tuple[float,float], base_point2: tuple[float,float], overlay_point1: tuple[float,float], overlay_point2: tuple[float,float], overlay_plane_size: tuple[float,float]) -> tuple[float, tuple[float,float], float]:
        """takes in two points to match from base and overlay and returns the rotation, translation and scale needed to match the two points"""
        if base_point1 == base_point2 or overlay_point1 == overlay_point2:
            return 0, (0,0), 1

        temp_translation = (base_point1[0]-overlay_point1[0],base_point1[1]-overlay_point1[1])
        temp_translated_overlay_point1, temp_translated_overlay_point2 = translate_points([overlay_point1, overlay_point2], temp_translation[0], temp_translation[1])

        rotation = calculate_point_angle(temp_translated_overlay_point1, base_point2,temp_translated_overlay_point2)
        overlay_point1, overlay_point2 = rotate_points([overlay_point1, overlay_point2], rotation, (overlay_plane_size[0]/2, overlay_plane_size[1]/2))

        distance_base = calculate_euclidean_distance(base_point1, base_point2)
        distance_overlay = calculate_euclidean_distance(overlay_point1, overlay_point2)
        scale = distance_base/distance_overlay

        overlay_point1 = (overlay_point1[0]*scale, overlay_point1[1]*scale)

        #translation must be recalculated after rotation and scaling
        translation = (base_point1[0]-overlay_point1[0],base_point1[1]-overlay_point1[1])

        return rotation, translation, scale
    
    def __calculate_drone_height(self, map_plane: Plane, photo_plane: Plane, map_point1: tuple[float,float], map_point2: tuple[float,float], photo_point1: tuple[float,float], photo_point2: tuple[float,float],) -> float:    
        """calculate drone height based on point locations"""
        map_distance = calculate_euclidean_distance(map_point1, map_point2)

        if photo_point1 == photo_point2:
            return 0
        
        camera_fov = 83
        camera_frame_diagonal_distance = calculate_euclidean_distance((0,0), photo_plane.size)
        points_diagonal_distance = calculate_euclidean_distance(photo_point1, photo_point2)

        points_vision_angle = camera_fov * (points_diagonal_distance / camera_frame_diagonal_distance)
        drone_height = map_distance / math.tan(math.radians(points_vision_angle))
        return drone_height
    
    def plot_map_and_photo(self,map_plane, photo_plane):
        map_points = map_plane.transformed_points
        photo_points = photo_plane.transformed_points

        plot = plt.plot([x[0] for x in map_points],[x[1] for x in map_points], 'ro', markersize=1)
        plot = plt.plot([x[0] for x in photo_points],[x[1] for x in photo_points], 'bo', markersize=1)

        return plot
