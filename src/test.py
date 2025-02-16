import numpy as np

# Helper function to compute cross product (to check for collinearity)
def cross_product(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

# Function to compute the distance between two 2D points (vectors)
def distance(p1, p2):
    return np.linalg.norm(np.array(p2) - np.array(p1))

# Main function to map collinear points in B to A
def map_collinear_points(list_a, list_b):
    new_list_a = list_a.copy()  # Create a copy of A for insertion

    for i in range(1, len(list_b) - 1):  # Skip the first and last points
        prev_b = list_b[i - 1]
        curr_b = list_b[i]
        next_b = list_b[i + 1]
        
        # Check if the current point in B is collinear with its neighbors
        vector1 = np.array(curr_b) - np.array(prev_b)
        vector2 = np.array(next_b) - np.array(curr_b)
        
        if cross_product(vector1, vector2) == 0:  # Collinear check using cross product
            # Find the corresponding neighbors in A
            prev_a = list_a[i - 1]
            next_a = list_a[i + 1]
            
            # Calculate distances between the current point's neighbors in B
            dist_b_prev = distance(prev_b, curr_b)
            dist_b_next = distance(curr_b, next_b)
            
            # Calculate the distances between the corresponding neighbors in A
            dist_a_prev = distance(prev_a, next_a)
            
            # Find the proportion of distances for inserting a point in A
            ratio_prev = dist_b_prev / (dist_b_prev + dist_b_next)
            
            # Insert a new point into A
            new_point = (1 - ratio_prev) * np.array(prev_a) + ratio_prev * np.array(next_a)
            new_list_a.insert(i, tuple(new_point))  # Insert the new point into list A

    return new_list_a

# Example usage:
list_a = [(0, 0), (1, 0), (1, 1), (0, 1)]  # A square
list_b = [(0, 0), (0.5, 0), (1, 0), (1, 0.5), (1, 1), (0.5, 1), (0, 1)]  # B with collinear points

mapped_a = map_collinear_points(list_a, list_b)
print("Mapped A:", mapped_a)
