from math import *

TRACKBALLSIZE = 0.8

def vzero( v ):
    v[0] = 0.
    v[1] = 0.
    v[2] = 0.

def vsub( v1, v2 ):
    return [v1[0]-v2[0],v1[1]-v2[1],v1[2]-v2[2]]

def vadd( v1, v2 ):
    return [v1[0]+v2[0],v1[1]+v2[1],v1[2]+v2[2]]

def vcross( v1, v2 ):
    cr = [0,0,0]
    cr[0] = (v1[1] * v2[2]) - (v1[2] * v2[1])
    cr[1] = (v1[2] * v2[0]) - (v1[0] * v2[2])
    cr[2] = (v1[0] * v2[1]) - (v1[1] * v2[0])
    return cr

def vlength( v ):
    return sqrt( v[0] * v[0] + v[1] * v[1] + v[2] * v[2] )

def vscale( v, div ):
    v[0] *= div
    v[1] *= div
    v[2] *= div

def vnormal( v ):
    vscale(v,1.0/vlength(v))

def vdot( v1, v2 ):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def vcopy( v1, v2 ):
    for i in range(3):
        v2[i]=v1[i]

def axis_to_quat( a, phi, q ):
    vnormal(a)
    vcopy(a,q)
    vscale(q,sin(phi/2.))
    q[3] = cos(phi/2.)

def tb_project_to_sphere( r, x, y ):
    d = sqrt(x*x + y*y)
    if (d < r*0.70710678118654752440):
        z = sqrt(r*r - d*d)
    else:
        t = r/1.41421356237309504880
        z = t*t/d
    return z

def trackball( q, p1x, p1y, p2x, p2y ):
    if (p1x == p2x and p1y == p2y):
        vzero(q)
        q[3] = 1.
        return q

    p1 = [p1x,p1y,tb_project_to_sphere(TRACKBALLSIZE,p1x,p1y)]
    p2 = [p2x,p2y,tb_project_to_sphere(TRACKBALLSIZE,p2x,p2y)]

    a = vcross(p2,p1)

    d = vsub(p1,p2)
    t = vlength(d) / (2.*TRACKBALLSIZE)

    if t > 1.:
        t = 1.
    if t < -1.:
        t = -1.

    phi = 2. * asin(t)

    axis_to_quat(a,phi,q)

    return q

global RENORM_MAX
global RENORM
RENORM_MAX = 97
RENORM = 0

def add_quats( q1, q2 ):
    t1,t2,t3,t4,tf=([0,0,0,0],[0,0,0,0],
                 [0,0,0,0],[0,0,0,0],[0,0,0,0])
    vcopy(q1,t1)
    vscale(t1,q2[3])

    vcopy(q2,t2)
    vscale(t2,q1[3])

    t3 = vcross(q2,q1)
    tf = vadd(t1,t2)
    tf = vadd(t3,tf)
    tf.append(0)
    tf[3] = q1[3] * q2[3] - vdot(q1,q2)
##    print
##    print 'tf',tf,q1,q2
##    print

    global RENORM_MAX
    global RENORM
    RENORM += 1
    if RENORM > RENORM_MAX:
        RENORM=0
        normalize_quat(tf)

    return tf

def normalize_quat( q ):
    mag = 0
    for i in range(4):
        mag+=q[i]*q[i]
    for i in range(4):
        q[i]/=mag

def build_rotmatrix( q ):
##    print 'quat to mat',q
    m = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    m[0][0] = 1.0 - 2.0 * (q[1] * q[1] + q[2] * q[2])
    m[0][1] = 2.0 * (q[0] * q[1] - q[2] * q[3])
    m[0][2] = 2.0 * (q[2] * q[0] + q[1] * q[3])
    m[0][3] = 0.0

    m[1][0] = 2.0 * (q[0] * q[1] + q[2] * q[3])
    m[1][1]= 1.0 - 2.0 * (q[2] * q[2] + q[0] * q[0])
    m[1][2] = 2.0 * (q[1] * q[2] - q[0] * q[3])
    m[1][3] = 0.0

    m[2][0] = 2.0 * (q[2] * q[0] - q[1] * q[3])
    m[2][1] = 2.0 * (q[1] * q[2] + q[0] * q[3])
    m[2][2] = 1.0 - 2.0 * (q[1] * q[1] + q[0] * q[0])
    m[2][3] = 0.0

    m[3][0] = 0.0
    m[3][1] = 0.0
    m[3][2] = 0.0
    m[3][3] = 1.0

    return m
        
        

