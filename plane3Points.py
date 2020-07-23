import numpy as np

class plane3Points:

  def __init__(self,points):
    p0, p1, p2 = points
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    x2, y2, z2 = p2

    ux, uy, uz = u = [x1-x0, y1-y0, z1-z0]
    vx, vy, vz = v = [x2-x0, y2-y0, z2-z0]

    u_cross_v = [uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx]

    self.planePoint  = np.array(p0)
    self.planeNormal = np.array(u_cross_v)

  def getIntersect(self,rayPoint, epsilon=1e-6):
        rayDirection = np.array([0,0,1])
        ndotu = self.planeNormal.dot(rayDirection)
        if abs(ndotu) < epsilon:
           return None
        w = rayPoint - self.planePoint
        si = -self.planeNormal.dot(w) / ndotu
        Psi = w + si * rayDirection + self.planePoint
        return Psi



if __name__=="__main__":

        planeTriangle = plane3Points([[0,0,100],[-100,100,200],[100,200,300]])

        #Define ray
        rayPoint = np.array([50, 50, 0]) #Any point along the ray

        Psi = planeTriangle.getIntersect(rayPoint)
        print ("intersection at", Psi)

