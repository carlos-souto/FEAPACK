import math
import gmsh
import feapack.gmsh
import feapack.model
import feapack.solver

#-----------------------------------------------------------
# PARAMETERS
#-----------------------------------------------------------

# geometry
W     = 45.0 # mm  | effective width
B     =  4.0 # mm  | thickness
an    =  9.0 # mm  | notch
p     =  2.0 # mm  | precrack
h     =  1.5 # mm  | envelope height
alpha = 30.0 # deg | envelope angle

# mesh
globalSeed           = 2.0
crackSeed            = 0.1
smoothingIterations  = 4
refinementIterations = 2
useQuads             = False
reducedIntegration   = False

# material and load
E  = 210000.0 # MPa | Young's modulus
nu = 0.3      # ... | Poisson's ratio
P  = 2000.0   # N   | load magnitude

# analysis
step = 150 # number of nodes to release in each iteration

# geometry checks (ASTM)
if not W >= 25.0:               raise ValueError('ASTM recommendation: W >= 25 mm')
if not W/20.0 <= B <= W/4.0:    raise ValueError('ASTM recommendation: W/20 <= B <= W/4')
if not an >= 0.2*W:             raise ValueError('ASTM recommendation: an >= 0.2W')
if not h <= W/16.0:             raise ValueError('ASTM recommendation: h <= W/16')
if not p >= max(0.1*B, h, 1.0): raise ValueError('ASTM recommendation: p >= max(0.1B, h, 1 mm)')
if not alpha <= 30.0:           raise ValueError('ASTM recommendation: alpha <= 30 deg')

#-----------------------------------------------------------
# CREATING THE MESH WITH GMSH
#-----------------------------------------------------------

# initialize Gmsh
gmsh.initialize()

# point coordinates
d = 0.25*W
a0 = an + p
outlineCoords = (
    (                                      0.0,   0.0), # 0
    (                                        p,   0.0), # 1
    (h/(2.0*math.tan(math.radians(alpha/2.0))), h/2.0), # 2
    (                              a0 + 0.25*W, h/2.0), # 3
    (                              a0 + 0.25*W, 0.6*W), # 4
    (                                   a0 - W, 0.6*W), # 5
    (                                   a0 - W,   0.0), # 6
)
holeCoords = (
    (        a0, 0.275*W),
    (a0 + d/2.0, 0.275*W),
    (a0 - d/2.0, 0.275*W),
)

# points
outlinePoints = [gmsh.model.geo.addPoint(x, y, 0.0, globalSeed) for x, y in outlineCoords]
holePoints = [gmsh.model.geo.addPoint(x, y, 0.0, globalSeed) for x, y in holeCoords]

# curves
outlineCurves = [gmsh.model.geo.addLine(outlinePoints[i], outlinePoints[i + 1]) for i in range(len(outlinePoints) - 1)] + \
    [gmsh.model.geo.addLine(outlinePoints[-1], outlinePoints[0])]
holeCurves = [
    gmsh.model.geo.addCircleArc(holePoints[1], holePoints[0], holePoints[2]),
    gmsh.model.geo.addCircleArc(holePoints[2], holePoints[0], holePoints[1]),
]

# curve loops
outlineLoop = gmsh.model.geo.addCurveLoop(outlineCurves)
holeLoop = gmsh.model.geo.addCurveLoop(holeCurves)

# surface
surface = gmsh.model.geo.addPlaneSurface([outlineLoop, holeLoop])

# geometry done
gmsh.model.geo.synchronize()

# create Gmsh physical groups that will become FEAPACK sets
# by default, Gmsh only saves elements associated with a physical group
# hence, a physical group specifying the domain is generally required
gmsh.model.addPhysicalGroup(2, [surface], name='PG-DOMAIN')          # contains the whole domain (a 2D surface)
gmsh.model.addPhysicalGroup(1, holeCurves, name='PG-HOLE')           # contains the hole edges (1D curves)
gmsh.model.addPhysicalGroup(1, [outlineCurves[-1]], name='PG-CRACK') # contains the crack path (a 1D curve)
gmsh.model.addPhysicalGroup(0, [outlinePoints[-1]], name='PG-FIXED') # contains the final crack path node (a 0D point)

# transfinite curves
gmsh.model.mesh.setTransfiniteCurve(outlineCurves[0], round(p/crackSeed))
gmsh.model.mesh.setTransfiniteCurve(outlineCurves[-1], round((W - a0)/crackSeed))

# generate and smooth 2D mesh
gmsh.model.mesh.generate(2)
gmsh.model.mesh.optimize(method='Laplace2D', niter=smoothingIterations)

# refine mesh
for _ in range(refinementIterations):
    gmsh.model.mesh.refine()
    gmsh.model.mesh.optimize(method='Laplace2D', niter=smoothingIterations)

# recombine mesh
if useQuads:
    gmsh.model.mesh.recombine()

# if you want to view the mesh now, uncomment the following line
# gmsh.fltk.run()

# write mesh to file
gmsh.option.setNumber('Mesh.SaveAll', False)          # default (also works with True, but more unused elements are saved)
gmsh.option.setNumber('Mesh.SaveGroupsOfNodes', True) # to save node sets
gmsh.write('advanced3.inp')

# finalize Gmsh
gmsh.finalize()

#-----------------------------------------------------------
# FINITE ELEMENT ANALYSIS WITH FEAPACK
#-----------------------------------------------------------

# create model database (MDB)
feapack.gmsh.clean('advanced3.inp') # required if inp file is generated by Gmsh
mdb = feapack.model.MDB.fromFile('advanced3.inp')

# print available sets
print('Node sets:', *mdb.nodeSets.keys())       # Node sets: PG-FIXED PG-HOLE PG-CRACK PG-DOMAIN
print('Element sets:', *mdb.elementSets.keys()) # Element sets: PG-DOMAIN

# create surface set for load application
mdb.surfaceSet(name='HOLE-SURFACE', surfaceNodes='PG-HOLE')

# create material and section
mdb.material(name='MATERIAL', young=E, poisson=nu)
mdb.section(
    name='SECTION',
    region='PG-DOMAIN',
    material='MATERIAL',
    type=feapack.model.SectionTypes.PlaneStress, # or simply 'PlaneStress'
    thickness=B,
    reducedIntegration=reducedIntegration
)

# create load
A = math.pi*d*B
mdb.surfaceTraction(name='LOAD', region='HOLE-SURFACE', y=P/A)

# boundary conditions
mdb.boundaryCondition(name='X-LOCK', region='PG-FIXED', u=0.0)
mdb.boundaryCondition(name='Y-LOCK', region='PG-CRACK', v=0.0)

# solve multiple jobs
# release crack nodes on each iteration
jobCount = 0                                                                         # job counter
crackNodes = [*mdb.nodeSets['PG-CRACK'].indices]                                     # unpack crack nodes into a list
crackNodes.sort(key=lambda index: mdb.mesh.nodes[index].x)                           # sort nodes by their X coordinate
crackTip = []                                                                        # crack tip
crackLength = []                                                                     # crack length
while len(crackNodes) > 0:                                                           # otherwise, full separation occurred
    crackTip.append(crackNodes[-1])                                                  # save current crack tip node index
    crackLength.append(a0 + abs(mdb.mesh.nodes[crackTip[-1]].x))                     # save current crack length
    mdb.nodeSets['PG-CRACK'] = feapack.model.NodeSet(crackNodes)                     # replace existing node set (update crack)
    feapack.solver.solve(mdb, analysis='static', jobName=f'advanced3_{jobCount:03}') # solve for current crack
    crackNodes = crackNodes[:-step]                                                  # remove nodes from crack closure (release)
    jobCount += 1                                                                    # increment job counter

# merge relevant output frames into a single output file
print('Merging output frames...')
feapack.model.ODB.merge(
    filePath='advanced3.out',
    selection=[(f'advanced3_{i:03}.out', [1]) for i in range(jobCount)],
    descriptions=[f'Step {i + 1}: Crack Length = {crackLength[i]:.3f}' for i in range(jobCount)],
    deleteExisting=True
)
print('Done')

#-----------------------------------------------------------
# VIRTUAL CRACK CLOSURE TECHNIQUE
#-----------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
print('VCCT post-processing...')

# load results
odb = feapack.model.ODB('advanced3.out', mode='read')
odb.goToFirstFrame()
Fy, Uy = [], []
for i in range(jobCount):
    Fy.append([*odb.getNodeOutputValues('Reaction Force>Reaction Force in Y')])
    Uy.append([*odb.getNodeOutputValues('Displacement>Displacement in Y')])
    odb.goToNextFrame()

# compute stress intensity factors
Ki = []
for i in range(jobCount - 1):
    da = crackLength[i + 1] - crackLength[i]
    fy = Fy[i][crackTip[i]]
    uy = Uy[i + 1][crackTip[i]]
    Gi = -(2.0*uy*fy)/(2.0*da)
    Ki.append(math.sqrt(Gi*E))

# "analytical" solution
a_ana = np.linspace(5.0, 40.0, 100)
Ki_ana = P/B*math.sqrt(math.pi/W)*(
     16.7*(a_ana/W)**(1/2) -
    104.7*(a_ana/W)**(3/2) +
    369.9*(a_ana/W)**(5/2) -
    573.8*(a_ana/W)**(7/2) +
    360.5*(a_ana/W)**(9/2)
)

# plot figure
plt.figure()
plt.xlabel('Crack Length [mm]')
plt.ylabel(r'Stress Intensity Factor [MPa⋅mm$^\text{1/2}$]')
plt.plot(crackLength[:-3], Ki[:-2], '-ok', label='VCCT')
plt.plot(a_ana, Ki_ana, '-r', label='Analytical')
plt.legend()
plt.savefig('advanced3.png')
print('Done')
