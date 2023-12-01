SPHERE_RADIUS = 1
MULTI_VALUES = ["SPHERE", "LIGHT", "RES", "BACK", "AMBIENT"]

"""
Reads the input file returns a dictionary with all values being in string
"""


def read_input():
    input = {}
    file = open(sys.argv[1], "r")

    for line in file:
        line = line.strip()
        # Split the line by tab character
        tokens = line.split('\t')

        # Further split each token by space and flatten the list
        split_tokens = [item for token in tokens for item in token.split() if item != '']

        if 0 < len(split_tokens) < 3:
            input[split_tokens[0]] = split_tokens[1]
        elif len(split_tokens) > 0 and split_tokens[0] != "SPHERE" and split_tokens[0] != "LIGHT":
            input[split_tokens[0]] = split_tokens[1:]
        elif len(split_tokens) > 0:
            if split_tokens[0] not in input:
                input[split_tokens[0]] = []
            input[split_tokens[0]].append(split_tokens[2:])

    file.close()
    return input


"""
Takes the input dictionary and returns an array of sphere objects
"""


def get_spheres(input):
    spheres_info = input["SPHERE"]
    spheres = []
    for sphere in spheres_info:
        temp = sp(sphere[0:3], sphere[3:6], sphere[6:9], sphere[9:13], sphere[13])
        spheres.append(temp)
    return spheres


"""
Takes the input dictionary and returns an array of light objects
"""


def get_lights(input):
    lights_info = input["LIGHT"]
    lights = []
    for l in lights_info:
        temp = Light(l[0:3], l[3:6])
        lights.append(temp)

    return lights


"""
Takes a ray object, sphere object, and a near plane variable
Returns a tuple consists of the scalar variable of the direction vector and a boolean
if both intersections are in front of the near plane then the boolean is true
false if the sphere is partially cut by the near plane.
"""


def intersect(ray, sphere, near):
    # inverse transposing the ray makes the calculations treat like a unit sphere
    transformed_origin = np.matmul(sphere.inv_transform, ray.origin)[:-1]  # non-homogenous
    transformed_direction = np.matmul(sphere.inv_transform, ray.direction)[:-1]  # non-homogenous

    # Coefficients for the quadratic equation
    a = np.dot(transformed_direction, transformed_direction)
    b = 2 * np.dot(transformed_direction, transformed_origin)
    c = np.dot(transformed_origin, transformed_origin) - 1.0

    discriminant = (b ** 2) - (4 * a * c)
    if discriminant > 0:
        # Calculate both intersections (if they exist)
        sqrt_discriminant = np.sqrt(discriminant)
        t1 = (-b - sqrt_discriminant) / (2 * a)
        t2 = (-b + sqrt_discriminant) / (2 * a)
        # Check if these intersections are in front of the ray
        t = min(t1, t2)

        if t1 > near and t2 > near:
            return t, False  # False if parts of sphere are not clipped by the near plane
        if t1 > near:
            return t1, True
        if t2 > near:
            return t2, True

    return None, False  # No intersection or behind the ray origin


"""
Parameters:
    intersection: vec4
    sphere: Sphere
    spheres: Sphere[]
    lights: Light[]
    la: vec3
    clipped: boolean
    
returns: 
    illum = ambient + diffuse + product
    0 <= illum <=1
"""


def color(intersection, sphere, spheres, lights, la, clipped):
    illum = sphere.ka * np.array(la) * sphere.color
    local_intersection = np.matmul(sphere.inv_transform, intersection - np.append(sphere.center, 1))
    N = np.matmul(sphere.inv_transform, local_intersection)[:-1]
    N /= np.linalg.norm(N)  # vec3

    for light in lights:

        if clipped:  # inside the sphere
            N = -N
            intersection = intersection + (np.append(N, 0) * 0.01)

        shadow_ray = Ray(intersection, light.vec4 - intersection)
        in_shadow = False
        for obstacle in spheres:
            shadow_t, _ = intersect(shadow_ray, obstacle, 0.001)
            if shadow_t is not None and shadow_t < 1:
                in_shadow = True

        if not in_shadow:
            L = (light.xyz - intersection[:-1]) / np.linalg.norm(light.xyz - intersection[:-1])  # vec3
            R = -2 * np.dot(N, -L) * N - L  # vec3
            V = (-intersection[:-1]) / np.linalg.norm(-intersection[:-1])  # vec3
            diffuse = light.intensity * sphere.kd * (max(np.dot(N, L), 0)) * sphere.color
            specular = light.intensity * sphere.ks * (max(np.dot(R, V), 0) ** sphere.n)

            illum += diffuse + specular
    return np.clip(illum, 0, 1)


"""
Parameters:
    ray: Ray
    spheres: Sphere[]
    near: int
    
Returns:
    (closest_object, intersection_point, clipped)
    closest_object: Sphere
    intersection_point: vec4
    clipped: boolean
"""


def closest_intersection(ray, spheres, near):
    closest_t = float('inf')
    closest_object = None
    intersection_point = None
    for sphere in spheres:
        t, clipped = intersect(ray, sphere, near)
        if t is not None and t < closest_t:
            intersection_point = (ray.origin + (t * ray.direction))
            closest_t = t
            closest_object = sphere

    return closest_object, intersection_point, clipped


"""
Parameters: 
    ray: Ray
    spheres: Sphere[]
    depth: int
    lights: light[]
    la: vec3
    near: int
    background: vec3

Returns:
    ads + reflected * (reflection_coefficient)
"""


def ray_trace(ray, spheres, depth, lights, la, near, background):
    if depth > 3:
        return np.array([0, 0, 0])
    closest_object, intersection_point, clipped = closest_intersection(ray, spheres, near)
    if intersection_point is None:
        return background

    local_intersection = np.matmul(closest_object.inv_transform,
                                   intersection_point - np.append(closest_object.center, 1))
    N = np.matmul(closest_object.inv_transform, local_intersection)[:-1]
    N /= np.linalg.norm(N)  # vec3

    reflection_direction = ray.direction[:-1] - 2 * (np.dot(ray.direction[:-1], N)) * N
    reflect_ray = Ray(intersection_point, np.append(reflection_direction, 0))
    reflected_color = ray_trace(reflect_ray, spheres, depth + 1, lights, la, 0.001, background)
    # if there is no intersection do not add the background color to the object
    if reflected_color.all() == background.all():
        reflected_color = 0
    pixel_color = color(intersection_point, closest_object, spheres, lights, la, clipped) + (
            reflected_color * closest_object.kr)
    return pixel_color


"""
Paramters:
    nCols: int
    nRows: int
    background: vec3
    spheres: Sphere[]
    near: int
    lights: Light[]
    la: vec3
    
Returns:
    image[600][600][3]
"""


def render(nCols, nRows, background, spheres, near, lights, la):
    image = np.zeros((nRows, nCols, 3), dtype=np.uint8)

    # Calculate the aspect ratio and the width of the plane
    # aspect_ratio = nCols / nRows
    # plane_height = 2 * np.tan(np.radians(50 / 2))
    # plane_width = plane_height * aspect_ratio

    for r in range(nRows):
        for c in range(nCols):
            # Adjusting the direction calculation to include aspect ratio
            x = 1.0 * (((2 * c) / nCols) - 1)  # * plane_width
            y = 1.0 * (((2 * r) / nRows) - 1)  # * plane_height
            direction = [x, -y, -near, 0]  # Negative y because pixel [0, 0] is top-left
            origin = [0, 0, 0, 1]
            ray = Ray(origin, direction)
            pixel_color = 255 * ray_trace(ray, spheres, 1, lights, la, near, background)

            image[r][c] = pixel_color

    return image


def write_ppm(image, filename):
    H, W, _ = image.shape
    with open(filename, 'w') as f:
        f.write(f'P3\n{W} {H}\n255\n')
        for row in image:
            for pixel in row:
                f.write(f'{pixel[0]} {pixel[1]} {pixel[2]} ')
            f.write('\n')


def main():
    input = read_input()
    spheres = get_spheres(input)

    lights = get_lights(input)
    H = float(input["TOP"])
    W = float(input["RIGHT"])
    N = float(input["NEAR"])
    bg = [float(bg_color) for bg_color in input["BACK"]]

    ambient = [float(a_color) for a_color in input["AMBIENT"]]
    image = render(int(input["RES"][0]), int(input["RES"][1]), np.array(bg), spheres, N, lights, ambient)
    write_ppm(image, "output/" + input["OUTPUT"])
    print("done")


if __name__ == "__main__":
    import sys
    import numpy as np
    from sphere import sphere as sp
    from light import Light
    from ray import Ray

    main()
