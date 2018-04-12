# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 10:05:54 2018

@author: Raluca Sandu
"""
import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#%%

X = np.array([[4,4], [5,5.5], [6, 4], [7, 5], [8,6.5 ], [9, 5]])
plt.figure()
t1 = plt.Polygon(X[:3,:], fill=False, edgecolor='Green', linewidth=2)
plt.gca().add_patch(t1)
plt.ylim([1, 12])
plt.xlim([1,12])
plt.show()

#%%
X, Y, Z= np.array([  -46.89300195,  -103.61379248, -1045.69018555])
Xv,Yv, Zv = np.array([  -47.58102053,  -107.70756127, -1044.90716196])

U,V,W =np.array([   -3.68100195 ,  -19.68279248, -1082.49243164])
Uv,Vv,Wv =np.array([   -6.77201399  , -25.47618886, -1078.44836744])

X1,Y1,Z1 = np.array([  -52.71000195,  -102.78279248, -1029.68920898])
U1,V1,W1 = np.array([    1.30499805 ,  -15.52779248, -1066.49145508])

X2,Y2,Z2  = np.array([  -63.51300195,   -95.30379248, -1056.89086914])
U2,V2,W2 = np.array([  -21.96300195,   -13.03479248, -1089.69287109])

soa = np.array([[0, 0, 1, 1, -2, 0], [0, 0, 2, 1, 1, 0],
                [0, 0, 3, 2, 1, 0], [0, 0, 4, 0.5, 0.7, 0]])


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
#ax.quiver(X, Y, Z, U, V, W)
ax.quiver(X, Y, Z, U, V, W, length=5, normalize=True)
ax.quiver(Xv, Yv, Zv, Uv, Vv, Wv, length=5, color='red',normalize=True)
#ax.quiver(X1, Y1, Z1, U1, V1, W1, length=15)
#ax.quiver(X2, Y2, Z2, U2, V2, W2, length=15)
#ax.set_xlim([-1, 0.5])
#ax.set_ylim([-1, 1.5])
#ax.set_zlim([-1, 8])
plt.show()