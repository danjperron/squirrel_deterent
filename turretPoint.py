from plane3Points import plane3Points
from Point import Point


class turretPoint:

    def __init__(self, screenX=1024, screenY=576, minDistance=10):
        self.screenX = screenX
        self.screenY = screenY
        self.minDistance = minDistance
        self.Table = []

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

        # now using 3 point surface figure out the x and y  turret
        # x axis first
        avgx = 0
        avgy = 0
        avgc = 0

        for x in range(2):
            pointx = []
            for i in range(x, x+3):
                pointx.append([dist_table[i][1][0],
                               dist_table[i][1][1],
                               dist_table[i][1][2]])
            planex = plane3Points(pointx)
            vx = planex.getIntersect([Target.x, Target.y, 0])
            print("vx {}".format(vx))
            if vx is None:
                continue

            # y axis firs t
            pointy = []
            for i in range(3):
                pointy.append([dist_table[i][1][0],
                               dist_table[i][1][1],
                               dist_table[i][1][3]])
            planey = plane3Points(pointy)
            vy = planey.getIntersect([Target.x, Target.y, 0])
            print("vy {}".format(vy))
            if vx is None:
                continue

            if vx[2] >= 0:
                if vx[2] <= 180:
                    if vy[2] >= 0:
                        if vy[2] <= 180:
                            avgx = avgx+vx[2]
                            avgy = avgy+vy[2]
                            avgc = avgc+1
        if avgc == 0:
            return None

        avgx = avgx / avgc
        avgy = avgy / avgc

        return Point(int(avgx), int(avgy))

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

