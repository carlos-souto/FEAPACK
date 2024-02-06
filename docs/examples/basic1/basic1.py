import math
import feapack.model
import feapack.solver

# defining the mesh
nodeData = (
    (77.0000,  0.0000, 0.0), #  0
    (80.0000,  0.0000, 0.0), #  1
    (75.5205, 15.0220, 0.0), #  2
    (78.4628, 15.6072, 0.0), #  3
    (71.1387, 29.4666, 0.0), #  4
    (73.9104, 30.6147, 0.0), #  5
    (64.0232, 42.7789, 0.0), #  6
    (66.5176, 44.4456, 0.0), #  7
    (54.4472, 54.4472, 0.0), #  8
    (56.5685, 56.5685, 0.0), #  9
    (42.7789, 64.0232, 0.0), # 10
    (44.4456, 66.5176, 0.0), # 11
    (29.4666, 71.1387, 0.0), # 12
    (30.6147, 73.9104, 0.0), # 13
    (15.0220, 75.5205, 0.0), # 14
    (15.6072, 78.4628, 0.0), # 15
    ( 0.0000, 77.0000, 0.0), # 16
    ( 0.0000, 80.0000, 0.0), # 17
    (78.5000,  0.0000, 0.0), # 18
    (79.6148,  7.8414, 0.0), # 19
    (76.9916, 15.3146, 0.0), # 20
    (76.6292,  7.5473, 0.0), # 21
    (76.5552, 23.2228, 0.0), # 22
    (72.5245, 30.0406, 0.0), # 23
    (73.6844, 22.3519, 0.0), # 24
    (70.5537, 37.7117, 0.0), # 25
    (65.2704, 43.6123, 0.0), # 26
    (67.9079, 36.2975, 0.0), # 27
    (61.8408, 50.7515, 0.0), # 28
    (55.5079, 55.5079, 0.0), # 29
    (59.5218, 48.8483, 0.0), # 30
    (50.7515, 61.8408, 0.0), # 31
    (43.6123, 65.2704, 0.0), # 32
    (48.8483, 59.5218, 0.0), # 33
    (37.7117, 70.5537, 0.0), # 34
    (30.0406, 72.5245, 0.0), # 35
    (36.2975, 67.9079, 0.0), # 36
    (23.2228, 76.5552, 0.0), # 37
    (15.3146, 76.9916, 0.0), # 38
    (22.3519, 73.6844, 0.0), # 39
    ( 7.8414, 79.6148, 0.0), # 40
    ( 0.0000, 78.5000, 0.0), # 41
    ( 7.5473, 76.6292, 0.0), # 42
)

elementData = (
    ('Plane8', ( 0,  1,  3,  2, 18, 19, 20, 21)), # 0
    ('Plane8', ( 2,  3,  5,  4, 20, 22, 23, 24)), # 1
    ('Plane8', ( 4,  5,  7,  6, 23, 25, 26, 27)), # 2
    ('Plane8', ( 6,  7,  9,  8, 26, 28, 29, 30)), # 3
    ('Plane8', ( 8,  9, 11, 10, 29, 31, 32, 33)), # 4
    ('Plane8', (10, 11, 13, 12, 32, 34, 35, 36)), # 5
    ('Plane8', (12, 13, 15, 14, 35, 37, 38, 39)), # 6
    ('Plane8', (14, 15, 17, 16, 38, 40, 41, 42)), # 7
)

mesh = feapack.model.Mesh(nodeData, elementData)

# create model database (MDB)
mdb = feapack.model.MDB(mesh)

# create node sets
mdb.nodeSet(name='nodes at x=0', indices=(node.index for node in mdb.mesh.nodes if node.x == 0.0))
mdb.nodeSet(name='nodes at y=0', indices=(node.index for node in mdb.mesh.nodes if node.y == 0.0))
mdb.nodeSet(name='nodes at r=77', indices=(node.index for node in mdb.mesh.nodes if abs(math.sqrt(node.x**2 + node.y**2) - 77.0) <= 0.001))

# create element set
mdb.elementSet(name='all elements', indices=range(mdb.mesh.elementCount))

# create surface set
mdb.surfaceSet(name='internal surface', surfaceNodes='nodes at r=77')

# create material and section
mdb.material(name='steel', young=210000.0, poisson=0.3)
mdb.section(
    name='steel section',
    region='all elements',
    material='steel',
    type=feapack.model.SectionTypes.PlaneStrain, # or simply 'PlaneStrain'
    thickness=1000.0,
    reducedIntegration=False
)

# create load
mdb.pressure(name='pressure load', region='internal surface', magnitude=8.0)

# create boundary conditions
mdb.boundaryCondition(name='x symmetry', region='nodes at x=0', u=0.0)
mdb.boundaryCondition(name='y symmetry', region='nodes at y=0', v=0.0)

# solve
feapack.solver.solve(mdb, analysis='static')
