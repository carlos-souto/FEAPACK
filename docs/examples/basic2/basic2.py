import feapack.model
import feapack.solver

# main guard required for multiprocessing
if __name__ == '__main__':

    # create model database (MDB)
    mdb = feapack.model.MDB.fromFile('basic2.inp')

    # create node sets
    mdb.nodeSet(name='nodes at x=0', indices=(node.index for node in mdb.mesh.nodes if node.x == 0.0))
    mdb.nodeSet(name='nodes at y=0', indices=(node.index for node in mdb.mesh.nodes if node.y == 0.0))
    mdb.nodeSet(name='nodes at x=100', indices=(node.index for node in mdb.mesh.nodes if node.x == 100.0))

    # create element set
    mdb.elementSet(name='all elements', indices=range(mdb.mesh.elementCount))

    # create surface set
    mdb.surfaceSet(name='loaded surface', surfaceNodes='nodes at x=100')

    # create material and section
    mdb.material(name='aluminum', young=70000.0, poisson=0.3)
    mdb.section(
        name='aluminum section',
        region='all elements',
        material='aluminum',
        type=feapack.model.SectionTypes.PlaneStress, # or simply 'PlaneStress'
        thickness=10.0,
        reducedIntegration=False
    )

    # create load
    mdb.surfaceTraction(name='applied tension', region='loaded surface', x=250.0)

    # boundary conditions
    mdb.boundaryCondition(name='x symmetry', region='nodes at x=0', u=0.0)
    mdb.boundaryCondition(name='y symmetry', region='nodes at y=0', v=0.0)

    # call solver inside main guard for multiprocessing
    # specifying processes > 1 will enable parallel mode
    feapack.solver.solve(mdb, analysis='static', processes=4)
