import json
import rhino3dm as rh
import compute_rhino3d.Curve 
import compute_rhino3d.Intersection as CI
import shapely.geometry as sh
import compute_rhino3d.Util
import time

compute_rhino3d.Util.authToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwIjoiUEtDUyM3IiwiYyI6IkFFU18yNTZfQ0JDIiwiYjY0aXYiOiI1dkllQnIxMWdJU2RIRGh3ZHQ2NXV3PT0iLCJiNjRjdCI6ImNyVm5hK29HbzZTaTZUVGVpNFQ3UFFkMVQrckdLdEx0cW9kWExBVWRJdGdSR0dGazdzNDNaWFRDdTJ6eFFaWGMxQ3ltc2VGbmNuTG4yNHlydkZNZkhHSkp2cjNMVFU3cjVoOXV2SkVLZkd5ZXE5NUZubmQ3LzVSd0k0aXBrbSs4SW92TVFqLzBFSFNSN0kzUXFQL3hLVFdmS1Z3eGgyYU9HdUVyMjJoOTlqdERKTXhVRHk1WGt0OUFyWFdjUjJ4dmJyM1A0RU43aS95SjN2UTNSb01TUXc9PSIsImlhdCI6MTU5ODAyODg1MX0.GUwrd4-gk9lVtV4u6PLF_Yqxhg7ZExDQ6GeNRgdnkkc'

def GetPolyline(pts):
    PtsList = rh.Point3dList()
    for p in pts:
        PtsList.Add(p.X, p.Y, p.Z)
    return rh.PolylineCurve(PtsList)

def GetShapelyPolygon(pts):
    poly = []
    for p in pts:
        pt = (p.X, p.Y)
        poly.append(pt)
    return sh.Polygon(poly[:-1])
    
def GetPucks(data, boundary):
    pucklines = []
    pucks = data['pucks']
    dist = []
    for puck in pucks:
        pts = []
        for p in puck:
            #pt = rh.Point3d(p[0], p[1], 0)
            pt = sh.Point(p[0], p[1]) 
            if boundary.contains(pt) == False: 
                pts.append(rh.Point3d(pt.x, pt.y, 0))
            else:
                pass
        for i in range(len(pts)-1):
            d = rh.Point3d.DistanceTo(pts[i], pts[i+1]) 
            dist.append(d)
        #pucklines.append(GetPolyline(pts))
        curve = GetPolyline(pts) 
        if curve.IsClosed:
            pucklines.append(curve)
        else:
            pass
    
    return pucklines, max(dist)
class BuiObj(object):
    def __init__(self, data, string):
        self.data = data
        self.string = string
    def GetPoints(self):
        newLst = []
        for d in self.data[self.string]:
            lst = []
            for k in d:
                lst.append(rh.Point3d(k[0], k[1], k[2]))
            newLst.append(lst)
        return newLst
    def GetLine(self):
        Allpts = self.GetPoints()
        pointList = rh.Point3dList()
        curves = []
        for pts in Allpts:
            if (pts[0].X == pts[-1].X) and (pts[0].Y == pts[-1].Y):
                pass
            else:
                pts.append(pts[0])
        for pts in Allpts:
            for p in pts:
                pointList.Add(p.X, p.Y, p.Z)
            curves.append(rh.PolylineCurve(pointList)) 
        return curves
    def GetDim(self, code, pts):
        dist = []
        for i in range(len(pts)-1):
            dist.append(rh.Point3d.DistanceTo(pts[i], pts[i+1]))
        if code == 'W':
            return (min(dist))
        else:
            return (max(dist))
    def AxialScale(self):
        Allpts = self.GetPoints()
        curves = []
        for pts in Allpts:
            pts.append(pts[0])
            minDist = self.GetDim('W', pts)
            new = []
            for i in range(len(pts)-1):
                dist = rh.Point3d.DistanceTo(pts[i], pts[i+1])
                if round(minDist, 3) == round(dist, 3):
                    mid = rh.Point3d((pts[i].X + pts[i+1].X)/2, (pts[i].Y + pts[i+1].Y)/2, 0)
                    vec1 = rh.Vector3d(pts[i+1].X-mid.X, pts[i+1].Y-mid.Y, 0)
                    n2 = rh.Point3d(pts[i+1].X + vec1.X, pts[i+1].Y + vec1.Y, 0)
                    n1 = rh.Point3d(pts[i].X - vec1.X, pts[i].Y - vec1.Y, 0)
                    #lst.append(rh.Point3d(pts[i].X + mid.X, pts[i].Y + mid.Y, 0))
                    #lst.append(rh.Point3d(pts[i+1].X + mid.X, pts[i+1].Y + mid.Y, 0))
                    new.append(n1)
                    new.append(n2)
                else:
                    pass
            new.append(new[0])
            curves.append(GetPolyline(new))
        return curves

def ReverseDirection(walls):
    reversed = []
    for w in walls:
        newpts = []
        para = compute_rhino3d.Curve.DivideByCount(w, 100, True) 
        for p in para:
            pt = rh.Curve.PointAt(w, p)
            newpts.append(pt)
        newpts.reverse()
        reversed.append(GetPolyline(newpts))
    return reversed

def GetCurveCenter(curve):
    x = []
    y = []
    z = []
    for c in curve.ToPolyline():
        x.append(c.X)
        y.append(c.Y)
        z.append(c.Z)
    x_avg = sum(x[1:])/len(x[1:])
    y_avg = sum(y[1:])/len(y[1:])
    z_avg = sum(z[1:])/len(z[1:])
    return rh.Point3d(x_avg, y_avg, z_avg)

def GetWalls(room, door, kitchen):
    params = []
    walls = []
    lengths = []
    pts = door.GetPoints()
    kitpts = kitchen.GetPoints()[0]
    for p in pts:
        lengths.append(round(door.GetDim('L', p), 3))
    lengths.append(round(kitchen.GetDim('L', kitpts), 3))
    scaleDoors = door.AxialScale()
    scaleDoors.append(kitchen.AxialScale()[0])
    for door in scaleDoors:
        events = CI.CurveCurve(door, room, 0.0000000001, 0.0)
        for event in events:
            params.append(event['ParameterB'])
    params.sort()
    curves = []
    params.append(params[0])
    params = params[1:]
    i = 0
    while i < len(params):
        if (params[i] < params[i+1]):
            curves.append(rh.Curve.Trim(room, params[i], params[i+1])) 
        else:
            curve1 = rh.Curve.Trim(room, params[i], 6)
            curve2 = rh.Curve.Trim(room, 0, params[i+1])
            join = compute_rhino3d.Curve.JoinCurves([curve1, curve2]) 
            for j in join:
                curves.append(j)
        i += 2
    for c in curves:
        if (compute_rhino3d.Curve.GetLength1(c, 0.01) < 24): 
            pass
        else:
            walls.append(c)
    return walls[1:]

def CreateOutlet(pts, width, height):
    rects = []
    for p in pts:
        pt = []
        pt.append(rh.Point3d(p.X - width/2, p.Y - height/2, 0))
        pt.append(rh.Point3d(p.X + width/2, p.Y - height/2, 0))
        pt.append(rh.Point3d(p.X + width/2, p.Y + height/2, 0))
        pt.append(rh.Point3d(p.X - width/2, p.Y + height/2, 0))
        pt.append(pt[0])
        rects.append(GetPolyline(pt)) 
    return rects

def WinCheck(window, wall):
    params = []
    win = window.AxialScale()[0]
    events =CI.CurveCurve(win, wall, 0.001, 0.0) 
    for event in events:
        params.append(event['ParameterB'])
        #curves = rh.Curve.Split(wall, params)
    return params

def PlaceOutlet(data, wall, window, boundary):
    ptsA = []
    ptsB = []
    
    for w in wall:
        #if wall length is less than 12 ft, only one outlet is necessary, which can be placed centrally or near enough
        if compute_rhino3d.Curve.GetLength1(w, 0.01) <= 144:
            para = compute_rhino3d.Curve.DivideByLength(w, compute_rhino3d.Curve.GetLength1(w, 0.01)/2.2, False)
            pt = rh.Curve.PointAt(w, para[0])
            ptsA.append(pt)
        else:
            #taking into account the tolerance of the pucks and adusting for outlets outside window
            maxD = (GetPucks(data, boundary)[1])
            para = list(compute_rhino3d.Curve.DivideByLength(w, (72-2*maxD), False))[::2] 
            #print(len(para))
            params = []
            inter = WinCheck(window, w)
            for p in para:
                if ((p >= inter[0]) and (p <= inter[1])):
                    params.append(inter[0] - 8/compute_rhino3d.Curve.GetLength1(w, 0.01))
                    params.append(inter[0] + 450/compute_rhino3d.Curve.GetLength1(w, 0.01))
                else:
                    params.append(p)
            for p in params:
                ptsB.append(rh.Curve.PointAt(w, p))
    return ptsA + ptsB 

def AreParallel(v1, v2):
    if (abs(v1.X*v2.Y) == abs(v2.X*v1.Y)):
        return True
    else:
        return False

def SolveInterference(outlets, pucks, wall):
    puckCen = []
    for p in pucks:
        puckCen.append(GetCurveCenter(p))
    cloud = rh.PointCloud(puckCen) 
    rects = []
    for o in outlets: 
        pts = []
        index = int(rh.PointCloud.ClosestPoint(cloud, GetCurveCenter(o))) 
        if compute_rhino3d.Curve.PlanarCurveCollision(o, pucks[index], rh.Plane.WorldXY(), 0.0001):  
            inter = CI.CurveCurve(o, pucks[index], 0.0001, 0.0) 
            for i in inter:
                #print(i)
                pts.append(i['PointA'])
            ptA = rh.Point3d(pts[0]['X'], pts[1]['Y'], 0)
            ptB = rh.Point3d(pts[1]['X'], pts[0]['Y'], 0)
           
            param = compute_rhino3d.Curve.ClosestPoint(wall, GetCurveCenter(o))[1]
            direction = rh.Curve.TangentAt(wall, param) 
            #print(GetShapelyPolygon(pucks[index].ToPolyline()))
            if GetShapelyPolygon(pucks[index].ToPolyline()).contains(sh.Point(ptA.X, ptA.Y)) == True:
                pt = ptA
            else:
                pt = ptB
            
            dir1 = rh.Vector3d(pt.X - pts[0]['X'], pt.Y - pts[0]['Y'], 0)
            dir2 = rh.Vector3d(pt.X - pts[1]['X'], pt.Y - pts[1]['Y'], 0)
            
            oc = o 
            if AreParallel(dir1, direction): 
                oc.Transform(rh.Transform.Translation(dir1.X, dir1.Y, 0)) 
            else:
                oc.Transform(rh.Transform.Translation(-dir2.X, -dir2.Y, 0))
            moved = oc
            rects.append(moved) 
        else:
            rects.append(o)
    
    return rects

def place_outlets(outlet_geom):
    outlets = []
    dict = {}
    for o in outlet_geom:
        outlets.append([GetCurveCenter(o).X, GetCurveCenter(o).Y, GetCurveCenter(o).Z])
    dict["outlets"] = outlets
    return dict

def main():
    start = time.time()

    filename = "json\studio_info.json"
    with open(filename, 'r') as f:
            studio_data = json.load(f)
    
    filename2 = "json/floor_info.json"
    with open(filename2, 'r') as f:
            floor_data = json.load(f)
    
    kitchen = BuiObj(studio_data, "kitchens")
    window = BuiObj(studio_data, 'windows')
    room = BuiObj(studio_data, 'generic_rooms')
    door = BuiObj(studio_data, 'doors')
    
    room_offset = compute_rhino3d.Curve.Offset(room.GetLine()[0], rh.Plane.WorldXY(), -6, 0.01, 1)[0]
    room_offset_sh = GetShapelyPolygon(room_offset.ToPolyline())
    puck = GetPucks(floor_data, room_offset_sh)[0]
    walls = GetWalls(room.GetLine()[0], door, kitchen)
    placeOutlets = PlaceOutlet(floor_data, walls, window, room_offset_sh)
    outlets = CreateOutlet(placeOutlets, 4, 4)

    final_geom = SolveInterference(outlets, puck, room.GetLine()[0])
    placeOutlets = place_outlets(final_geom)
    
    file = 'outlets.json'
    with open(file, 'w') as json_out:
        json.dump(placeOutlets, json_out)
    
    end = time.time()
    print(end - start)

if __name__ == "__main__":
    main()


