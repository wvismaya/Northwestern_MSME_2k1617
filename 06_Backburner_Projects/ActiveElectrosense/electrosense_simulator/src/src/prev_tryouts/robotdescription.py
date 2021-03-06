#!/usr/bin/env python

import rospy
import numpy as np
from math import atan2, pi
import hdt_nri_description.msg as hnd
import robot_calc_functions as r
import random

#Define lengths from tank to palm0.0
# Tank
# Fixed
# Roll of Pi/2
x_tank = 0
y_tank = 0
z_tank = 0

# Gantry Mounting Plate
# Fixed
x_mount = 0
y_mount = 0.952
z_mount = -0.5

# Gantry_x
# Prismatic
x_gantry_x = 0.0
y_gantry_x = 0.1035
z_gantry_x = 0.0

# Gantry_y
# Prismatic
x_gantry_y = 0.0
y_gantry_y = 0.1472
z_gantry_y = 0.0

# Gantry_z
# Prismatic
x_gantry_z = 0.1
y_gantry_z = 0.650
z_gantry_z = 0.161

# Gantry_Yaw
# Revolute
# ROLL OF PI!
x_gantry_yaw = 0.0
y_gantry_yaw = -1.223
z_gantry_yaw = 0.23

# Joint1
# R -2.094 to 2.094
x_j1 = 0.0
y_j1 = -0.068
z_j1 = 0.0

# Joint1_FIXED
# Fixed
x_j1f = 0.0
y_j1f = -0.0865
z_j1f = 0.0

# Joint2
# R -pi/2 to pi/2
x_j2 = 0.02393
y_j2 = -0.0510
z_j2 = 0.0

# Joint0.0
# R -pi/2 to pi/2
x_j3 = -0.02395
y_j3 = -0.08200
z_j3 = -0.0279

# Lengths of fingers
len_finger = 0.7 - 0.632
len_thumb = 0.77-0.64
len_palm = 0.15 #0.08 + 0.25

# Palm
# Fixed
# Considering axis of Index finger for palm
x_palm = 0.0
## 0.116 = (y_index - y_thumb)/2 + (y_palm - y_thumb)
y_palm = -0.07
z_palm = 0.028

x_thumb_base = -0.0000362
y_thumb_base = -0.0580
z_thumb_base =  0.017785

x_thumb = 0.00879
y_thumb = -0.021848
z_thumb =  0.057028

x_index = -0.0000362
y_index = -0.165998
z_index = 0.0357953

x_ring = -0.0000362
y_ring = -0.165998
z_ring = -0.0182153

#Define offsets
x_off = 0.1 #x_j1 + x_gantry_yaw + x_gantry_z + x_gantry_y + x_gantry_x + x_mount + x_tank
y_off = 0.177 #y_j1 + y_gantry_yaw + y_gantry_z + y_gantry_y + y_gantry_x + y_mount + y_tank
z_off = 0.629 #z_j1 + z_gantry_yaw + z_gantry_z + z_gantry_y + z_gantry_x + z_mount + z_tank

def get_offsets():
    return [x_off, y_off, z_off]

x_m = (x_palm + x_j3 + x_j2 + x_j1f) #+ x_j1) #+ x_gantry_yaw + x_gantry_z + x_gantry_y + x_gantry_x + x_mount + x_tank
y_m = (y_palm + y_j3 + y_j2 + y_j1f) #+ y_j1) #+ y_gantry_yaw + y_gantry_z + y_gantry_y + y_gantry_x + y_mount + y_tank
z_m = (z_palm + z_j3 + z_j2 + z_j1f) #+ z_j1) #+ z_gantry_yaw + z_gantry_z + z_gantry_y + z_gantry_x + z_mount + z_tank

M_index = [ 
[1, 0, 0, -x_m - x_index ],
[0, 1, 0, -y_m - y_index + len_finger ],
[0, 0, 1, z_m + z_index ],
[0,0,0,1]
]

M_ring = [
[1, 0, 0, -x_m - x_ring ],
[0, 1, 0, -y_m - y_ring + len_finger],
[0, 0, 1, z_m + z_ring ],
[0,0,0,1]
]

M_thumb = [
[1, 0, 0, -x_m - x_thumb_base],
[0, 1, 0, -y_m - y_thumb_base],
[0, 0, 1, z_m + z_thumb_base + len_thumb ],
[0,0,0,1]
]

M_palm = [ 
[1, 0, 0, -x_m],
[0, 1, 0, -y_m + len_palm],
[0, 0, 1, z_m],
[0,0,0,1]
]

def blist_finger(zfinger, yfinger,xfinger, n):
    Blist = [ 
    [0, 1, 0, n*(z_palm + z_j3 + z_j2 + zfinger), 0, n*(x_palm + x_j3 + x_j2 + xfinger)],
    [1, 0, 0, 0, n*(z_palm + z_j3 + zfinger), n*(y_palm + y_j3 + yfinger + len_finger)],
    [0, 0, 1, n*(y_palm + yfinger + len_finger), n*(x_palm + xfinger), 0],
    [0, 0, 1, 0, n*(len_finger), 0]]
    return Blist

n = -1
Blist_index = blist_finger(z_index, y_index, x_index, n)
Blist_ring = blist_finger(z_ring, y_ring, x_ring, n)

Blist_thumb = [
[0, 1, 0, n*(z_palm + z_j3 + z_j2 + z_thumb_base + len_thumb), 0, n*(x_palm + x_j3 + x_j2 + x_thumb_base)],
[1, 0, 0, 0, n*(z_palm + z_j3 + z_thumb_base + len_thumb), n*(y_palm + y_j3 + y_thumb_base)],
[0, 0, 1, n*(y_palm + y_thumb_base), n*(x_palm + x_thumb_base), 0],
[0, 1, 0, n*len_thumb, 0, 0]]

Blist_palm = [
[0, 1, 0, n*(z_palm + z_j3 + z_j2 + z_j1f), 0, n*(x_palm + x_j3 + x_j2 + x_j1f)],
[1, 0, 0, 0, n*(z_palm + z_j3), n*(y_palm + y_j3 + len_palm)],
[0, 0, 1, (n*(y_palm) + len_palm), n*(x_palm), 0],
]
#(n*(len_finger/4))

maxtime = 5

def get_angles_thumb(blist, mhome, xg, yg, zg):
    Blist = blist
    M = mhome

    i = 1
    oldresult = 10
    goalpoint = np.array([xg,yg,zg,1])
    
    T = [[1,0,0,xg], [0,1,0,yg], [0,0,1,zg], [0,0,0,1]]

    # gantry_x, gantry_y, gantry_z, gantry_yaw, j1, j2, j3
    thetalist0 =[0,0,0, 0]
    eomg = 0.01
    ev = 0.01
    [thetalist,success] = r.IKinBody2(Blist, M, T, thetalist0, eomg, ev)
    reachedpoint_old = r.FKinBody(M,Blist,thetalist)[:,3]
    reachedpoint = np.array([i + j for i, j in zip(reachedpoint_old, [x_off, y_off, z_off, 0])])
    result = np.around(np.linalg.norm(goalpoint - reachedpoint) * 1000) / 1000.0
    print result
    return thetalist

def get_angles_finger(blist, mhome, xg, yg, zg):
    Blist = blist
    M = mhome

    i = 1
    oldresult = 10
    goalpoint = np.array([xg,yg,zg,1])
    
    T = [[1,0,0,xg], [0,1,0,yg], [0,0,1,zg], [0,0,0,1]]
    print T

    # gantry_x, gantry_y, gantry_z, gantry_yaw, j1, j2, j3
    thetalist0 =[0,0,0, 0]
    eomg = 0.1
    ev = 0.01
    [thetalist,success] = r.IKinBody(Blist, M, T, thetalist0, eomg, ev)
    reachedpoint_old = r.FKinBody(M,Blist,thetalist)[:,3]
    reachedpoint = np.array([i + j for i, j in zip(reachedpoint_old, [x_off, y_off, z_off, 0])])
    result = np.around(np.linalg.norm(goalpoint - reachedpoint) * 1000) / 1000.0
    print reachedpoint
    return thetalist

def ik_index(xg, yg, zg):
    goalpoint = np.array([xg,yg,zg])
    
    T = [[1,0,0,xg], [0,1,0, yg], [0,0,1,zg], [0,0,0,1]]
    print 'To reach'
    print goalpoint

    # gantry_x, gantry_y, gantry_z, gantry_yaw, j1, j2, j3
    thetalist0 =[-0.1,0.1,-0.1, 0.1]
    eomg = 0.01
    ev = 0.001
    [thetalist,success] = r.IKinBody2(Blist_index, M_index, T, thetalist0, eomg, ev)
    reachedpoint_old = r.FKinBody(M_index,Blist_index,thetalist)[0:3,3]
    reachedpoint = np.array([i + j for i, j in zip(reachedpoint_old, [x_off, y_off, z_off])])
    #result = np.around(np.linalg.norm(goalpoint - reachedpoint) * 1000) / 1000.0
    print 'Reached Now'
    print reachedpoint
    return thetalist

def fk_index(thetalist):
    T_old = r.FKinBody(M_index, Blist_index, thetalist)[0:3,3]
    T = np.array([i + j for i, j in zip(T_old, [x_off, y_off, z_off])])
    #print T
    return T

def fk_ring(thetalist):
    T_old = r.FKinBody(M_ring, Blist_ring, thetalist)[0:3,3]
    T = np.array([i + j for i, j in zip(T_old, [x_off, y_off, z_off])])
    print 'old ring'
    print T_old
    print 'offsets'
    print [x_off, y_off, z_off]
    return T

def fk_thumb(thetalist):
    T_old = r.FKinBody(M_thumb, Blist_thumb, thetalist)[0:3,3]
    T = np.array([i + j for i, j in zip(T_old, [x_off, y_off, z_off])])
    return T

def fk_palm(thetalist):
    T_old = r.FKinBody(M_palm, Blist_palm, thetalist)[0:3,3]
    T = np.array([i + j for i, j in zip(T_old, [x_off, y_off, z_off])])
    #print 'old palm'
    #print T_old
    #print 'offsets'
    #print [x_off, y_off, z_off]
    return T