![testAnother](https://github.com/KantasOnur/RayTracer/assets/43832033/428a5e2d-d65c-4e27-a95b-5fbc09682dea)
# Overview
RayTracer is a ray tracing engine that takes a text file as input and outputs a ppm file.
# How It Works
RayTracer operates by calculating the color of each pixel, taking into consideration factors like lighting, shadows, and reflections. The program runs on single thread, and written in python, so it can take a while for images to render. ```testRaindow.txt``` takes the longest, around a minute. Utilizing multi-threading would have been more efficient as each pixel is independent of each other.
Key features include:
- **_Phong Illumination:_** Utilizes this model for realistic rendering of light and shadow.
- **_Local Illumination:_** The engine focuses on local illumination without global illumination techniques.
- **_Shadow Implementation:_** Shadows are calcualted by checking whether a point on a sphere is blocked by another object from a light source.
- **_Edge Cases:_** Cases where light is inside of a sphere and cut open by the near plane is considered. ```testIllum.txt```, no light goes through inside of objects.
# Input Text Format
- NEAR n 
- LEFT l 
- RIGHT r 
- BOTTOM b 
- TOP t 
- RES x y 
- SPHERE name x* y* z* sx* sy* sz* r** g** b** ka** kd** ks** kr** n
- LIGHT name x* y* z* ir** ig** ib**
- BACK r** g** b**
- AMBIENT ir** ig** ib**
- OUTPUT name (string)

# Important
**Simplified View Frustum:** The parameters for left, right, bottom, and top are set to -1 and 1 by default. Adjusting these values involves changing a few variables in the code.

# Input Valus Types:
- **_Integers:_** Default type without labels.
- **_Floats:_** Marked with a single asterisk (*).
- **_Normalized Floats:_** Floats between 0 and 1, indicated by double asterisks (**).

# Variable Names:
- **_s(xyz):_** Scalar components of the sphere, can be non-uniform.
- **_ka:_** Ambient coefficient.
- **_kd:_** Diffuse coefficient.
- **_ks:_** Specular coefficient.
- **_kr:_** Reflection coefficient.
- **_n:_** Specular exponent.
- **_i(rgb):_** Light intensity in red, green, and blue.
