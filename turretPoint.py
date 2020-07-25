from plane3Points import plane3Points
from Point import Point


class turretPoint:

    def __init__(self, screenX=1024, screenY=576, minDistance=10):
        self.screenX = screenX
        self.screenY = screenY
        self.minDistance = minDistance
        self.Table = []


    # A utility function to calculate area
    # of triangle formed by (x1, y1),
    # (x2, y2) and (x3, y3)
    def area(self, x1, y1, x2, y2, x3, y3):
        return abs((x1 * (y2 - y3) + x2 * (y3 - y1)
                   + x3 * (y1 - y2)) / 2.0)


    # A function to check whether point P(x, y)
    # lies inside the triangle formed by
    # A(x1, y1), B(x2, y2) and C(x3, y3)
    def isInsideTriangle(self,
                          x1, y1, x2, y2, x3, y3, x, y):
        # Calculate area of triangle ABC
        A = self.area(x1, y1, x2, y2, x3, y3)
        # Calculate area of triangle PBC
        A1 = self.area(x, y, x2, y2, x3, y3)
        # Calculate area of triangle PAC
        A2 = self.area(x1, y1, x, y, x3, y3)
        # Calculate area of triangle PAB
        A3 = self.area(x1, y1, x2, y2, x, y)
        # Check if sum of A1, A2 and A3
        # is same as A
        if(A == A1 + A2 + A3):
            return True
        else:
            return False


    # combinational sort algorithm
    # return next smallest by smallest combination first

    def combin3(self,table):
       if table is None:
          table = [0, 1 , 2 ]
          return table
       table[1] = table[1] + 1
       if table[1] >= table[2]:
          table[0] = table[0] + 1
          table[1] = table[0] + 1
          if table[0] >= table[2]-1:
            table[0]=0
            table[1]=1
            table[2]= table[2] + 1
            return table
       return table




    def Find(self, Target):
        if len(self.Table) < 3:
            return None
        if Target is None:
            return None
        # create another table with distance
        dist_table = []
        for i in self.Table:
             p = Point(i[0], i[1])
             dist = Target.Distance(p)
             dist_table.append((dist, i))

        #  sort table  by distance
        for i in range(len(dist_table)):
            for j in range(i+1, len(dist_table)-1):
                if dist_table[i][0] > dist_table[j][0]:
                    tempo = dist_table[i]
                    dist_table[i] = dist_table[j]
                    dist_table[j] = tempo

        #  from sorted table find  nearest triangle which contains the point
        # I'm using  combination algorithm from small to large
        TPoint = [0, 1 , 2]

        while True:
            if self.isInsideTriangle(dist_table[TPoint[0]][1][0], dist_table[TPoint[0]][1][1],
                                     dist_table[TPoint[1]][1][0], dist_table[TPoint[1]][1][1],
                                     dist_table[TPoint[2]][1][0], dist_table[TPoint[2]][1][1],
                                     Target.x, Target.y):
                break
            #  using combination algorithm index
            #  to always use the smallest distance first
            self.combin3(TPoint)
            if TPoint[2] >= len(dist_table):
                TPoint = [0, 1, 2]
                break

        # ok now let's get the X and Y turret value from the best triangle we found

        pointx = []
        for i in TPoint:
            pointx.append([dist_table[i][1][0],
                           dist_table[i][1][1],
                           dist_table[i][1][2]])
        planex = plane3Points(pointx)
        vx = planex.getIntersect([Target.x, Target.y, 0])
        # print("vx {}".format(vx))
        if vx is None:
            return None

        # y axis firs t
        pointy = []
        for i in TPoint:
            pointy.append([dist_table[i][1][0],
                           dist_table[i][1][1],
                           dist_table[i][1][3]])
        planey = plane3Points(pointy)
        vy = planey.getIntersect([Target.x, Target.y, 0])
        # print("vy {}".format(vy))
        if vy is None:
            return None
        return Point(int(vx[2]), int(vy[2]))

    def Add(self, ScreenP, TurretP):
        # first erase point near 10 pixels
        for i in self.Table:
            p = Point(i[0], i[1])
            if ScreenP.Distance(p) < self.minDistance:
                self.Table.remove(i)

        # add current
        self.Table.append((ScreenP.x, ScreenP.y, TurretP.x, TurretP.y))

    def Save(self, filename="turretTable.cfg"):
        file = open(filename, "wt")
        file.write("Screen X\tScreen Y\tTurret X\tTurret Y\n")
        for i in self.Table:
            file.write("{}\t{}\t{}\t{}\n".format(i[0]/float(self.screenX),
                                                 i[1]/float(self.screenY),
                                                 int(i[2]), int(i[3])))
        file.close()

    def Load(self, filename="turretTable.cfg"):
        self.Table = []
        try:
            file = open(filename, "rt")
            lines = file.read()
            file.close()
            line = lines.split('\n')
            for i in line[1:]:
                splitline = i.split('\t')
                if len(splitline) == 4:
                    try:
                        point = [int(float(splitline[0]) * self.screenX + 0.4),
                                 int(float(splitline[1]) * self.screenY + 0.4),
                                 int(splitline[2]), int(splitline[3])]
                        self.Table.append(point)
                    except ValueError:
                        continue
        except IOError:
            pass

