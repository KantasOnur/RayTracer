import numpy as np


class sphere:

    def __init__(self, position, scale, color, k, n):
        self.x = float(position[0])
        self.y = float(position[1])
        self.z = float(position[2])

        self.center = np.array([self.x, self.y, self.z])

        self.sx = float(scale[0])
        self.sy = float(scale[1])
        self.sz = float(scale[2])

        self.scaling = np.array([self.sx, self.sy, self.sz])

        self.r = float(color[0])
        self.g = float(color[1])
        self.b = float(color[2])

        self.color = np.array([self.r, self.g, self.b])

        self.ka = float(k[0])
        self.kd = float(k[1])
        self.ks = float(k[2])
        self.kr = float(k[3])

        self.n = int(n)

        self.transform = self.__compute_transform()
        self.inv_transform = np.linalg.inv(self.transform)

    def __repr__(self):
        pos = f"pos:({self.x},{self.y},{self.z})"
        scale = f"scale:({self.sx},{self.sy},{self.sz})"
        color = f"color: {self.r, self.g, self.b}"
        k = f"k(s):({self.ka},{self.kd},{self.ks},{self.kr})"
        n = f"n:{self.n}"

        return pos + " " + scale + " " + color + " " + k + " " + n

    def __compute_transform(self):
        transform = np.identity(4)

        # Apply scaling
        for i in range(3):
            transform[i, i] = self.scaling[i]

        # Apply translation
        transform[:3, 3] = self.center
        return transform

    def __eq__(self, other):
        return (self.center == other.center).all() and (self.scaling == other.scaling).all()
