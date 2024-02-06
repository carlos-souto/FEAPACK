import feapack.model
import feapack.solver

# main guard required for multiprocessing
if __name__ == '__main__':

    # create model database (MDB)
    mdb = feapack.model.MDB.fromFile('basic4.inp')

    # create sets
    mdb.nodeSet(
        name='side nodes',
        indices=(node.index for node in mdb.mesh.nodes if abs(node.x) == 100.0 or abs(node.y) == 90.0)
    )

    mdb.elementSet(
        name='all elements',
        indices=range(mdb.mesh.elementCount)
    )

    # create material and section
    mdb.material(name='steel', young=210000.0, poisson=0.3, density=7.85e-9) # density required for frequency analysis

    mdb.section(
        name='steel section',
        region='all elements',
        material='steel',
        type=feapack.model.SectionTypes.General, # or simply 'General'
        reducedIntegration=False
    )

    # create boundary condition
    mdb.boundaryCondition(name='fixed sides', region='side nodes', u=0.0, v=0.0, w=0.0)

    # call solver inside main guard for multiprocessing
    # specifying processes > 1 will enable parallel mode
    # k0 specifies the requested number of eigenvalues and corresponding eigenvectors
    feapack.solver.solve(mdb, analysis='frequency', k0=10, processes=4)
