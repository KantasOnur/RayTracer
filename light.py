import numpy as np


class Light:

    def __init__(self, pos, intensity):
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.z = float(pos[2])

        self.ir = float(intensity[0])
        self.ig = float(intensity[1])
        self.ib = float(intensity[2])

        self.intensity = np.array([self.ir, self.ig, self.ib])
        self.vec4 = np.array([self.x, self.y, self.z, 1])
        self.xyz = np.array([self.x, self.y, self.z])

    def __repr__(self):
        pos = f"{self.x, self.y, self.z}"
        intensity = f"{self.ir, self.ig, self.ib}"

        return f"pos: {pos} intensity: {intensity}"
