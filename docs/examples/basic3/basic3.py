import feapack.model
import feapack.solver

# main guard required for multiprocessing
if __name__ == '__main__':

    # create model database (MDB)
    mdb = feapack.model.MDB.fromFile('basic3.inp')

    # node sets and element sets are defined in the 'basic3.inp' file
    # set names are automatically converted to upper case (technical limitation)
    print('Node sets:', *mdb.nodeSets.keys())       # Node sets: INTERNAL-SURFACE-NODES BASE-NODES
    print('Element sets:', *mdb.elementSets.keys()) # Element sets: ALL-ELEMENTS

    # however, surface sets in FEAPACK have their own format, so they have to be created here
    mdb.surfaceSet(name='INTERNAL-SURFACE', surfaceNodes='INTERNAL-SURFACE-NODES')

    # create material and section
    mdb.material(name='STEEL', young=210000.0, poisson=0.3, density=7.85e-9) # density required for gravity load
    mdb.section(
        name='STEEL-SECTION',
        region='ALL-ELEMENTS',
        material='STEEL',
        type=feapack.model.SectionTypes.Axisymmetric, # or simply 'Axisymmetric'
        reducedIntegration=False
    )

    # create loads
    mdb.acceleration(name='GRAVITY', region='ALL-ELEMENTS', y=-9806.65)
    mdb.pressure(name='INTERNAL-PRESSURE', region='INTERNAL-SURFACE', magnitude=8.0)

    # create boundary condition
    mdb.boundaryCondition(name='FIXED-BASE', region='BASE-NODES', u=0.0, v=0.0)

    # call solver inside main guard for multiprocessing
    # specifying processes > 1 will enable parallel mode
    feapack.solver.solve(mdb, analysis='static', processes=4)
