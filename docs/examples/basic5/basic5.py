import feapack.model
import feapack.solver

# create model database (MDB)
mdb = feapack.model.MDB.fromFile('basic5.inp')

# create node sets
mdb.nodeSet(name='nodes at y = 0', indices=(node.index for node in mdb.mesh.nodes if node.y == 0.0))
mdb.nodeSet(name='nodes at y = 1000', indices=(node.index for node in mdb.mesh.nodes if node.y == 1000.0))

# create element set
mdb.elementSet(name='all elements', indices=range(mdb.mesh.elementCount))

# create surface set
mdb.surfaceSet(name='top surface', surfaceNodes='nodes at y = 1000')

# create material and section
mdb.material(name='steel', young=210000.0, poisson=0.3)
mdb.section(
    name='steel section',
    region='all elements',
    material='steel',
    type=feapack.model.SectionTypes.PlaneStress, # or simply 'PlaneStress'
    reducedIntegration=False
)

# create load
mdb.pressure(name='unit pressure', region='top surface', magnitude=1.0)

# create boundary condition
mdb.boundaryCondition(name='fixed base', region='nodes at y = 0', u=0.0, v=0.0)

# call solver
# k0 specifies the requested number of eigenvalues and corresponding eigenvectors
feapack.solver.solve(mdb, analysis='buckling', k0=10)
