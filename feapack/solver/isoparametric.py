import numpy as np
import feapack.solver.linearAlgebra as linalg
from feapack.typing import Real, RealVector, RealMatrix
from feapack.model import Element, Surface, ElementTypes, SectionTypes, ModelingSpaces
from typing import Literal

def nodes(element: Element | Surface) -> RealMatrix:
    """Returns a matrix containing the natural nodal coordinates for the specified element type."""
    match element.type:
        case ElementTypes.Line2:
            return np.array((
                (-1.0, 0.0, 0.0),
                ( 1.0, 0.0, 0.0),
            ), dtype=Real)
        case ElementTypes.Line3:
            return np.array((
                (-1.0, 0.0, 0.0),
                ( 1.0, 0.0, 0.0),
                ( 0.0, 0.0, 0.0),
            ), dtype=Real)
        case ElementTypes.Plane3:
            return np.array((
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
            ), dtype=Real)
        case ElementTypes.Plane4:
            return np.array((
                (-1.0, -1.0, 0.0),
                ( 1.0, -1.0, 0.0),
                ( 1.0,  1.0, 0.0),
                (-1.0,  1.0, 0.0),
            ), dtype=Real)
        case ElementTypes.Plane6:
            return np.array((
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (0.5, 0.0, 0.0),
                (0.5, 0.5, 0.0),
                (0.0, 0.5, 0.0),
            ), dtype=Real)
        case ElementTypes.Plane8:
            return np.array((
                (-1.0, -1.0, 0.0),
                ( 1.0, -1.0, 0.0),
                ( 1.0,  1.0, 0.0),
                (-1.0,  1.0, 0.0),
                ( 0.0, -1.0, 0.0),
                ( 1.0,  0.0, 0.0),
                ( 0.0,  1.0, 0.0),
                (-1.0,  0.0, 0.0),
            ), dtype=Real)
        case ElementTypes.Volume4:
            return np.array((
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (0.0, 0.0, 1.0),
            ), dtype=Real)
        case ElementTypes.Volume6:
            return np.array((
                (0.0, 0.0, -1.0),
                (1.0, 0.0, -1.0),
                (0.0, 1.0, -1.0),
                (0.0, 0.0,  1.0),
                (1.0, 0.0,  1.0),
                (0.0, 1.0,  1.0),
            ), dtype=Real)
        case ElementTypes.Volume8:
            return np.array((
                (-1.0, -1.0, -1.0),
                ( 1.0, -1.0, -1.0),
                ( 1.0,  1.0, -1.0),
                (-1.0,  1.0, -1.0),
                (-1.0, -1.0,  1.0),
                ( 1.0, -1.0,  1.0),
                ( 1.0,  1.0,  1.0),
                (-1.0,  1.0,  1.0),
            ), dtype=Real)
        case ElementTypes.Volume10:
            return np.array((
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (0.0, 1.0, 0.0),
                (0.0, 0.0, 1.0),
                (0.5, 0.0, 0.0),
                (0.5, 0.5, 0.0),
                (0.0, 0.5, 0.0),
                (0.0, 0.0, 0.5),
                (0.5, 0.0, 0.5),
                (0.0, 0.5, 0.5),
            ), dtype=Real)
        case ElementTypes.Volume15:
            return np.array((
                (0.0, 0.0, -1.0),
                (1.0, 0.0, -1.0),
                (0.0, 1.0, -1.0),
                (0.0, 0.0,  1.0),
                (1.0, 0.0,  1.0),
                (0.0, 1.0,  1.0),
                (0.5, 0.0, -1.0),
                (0.5, 0.5, -1.0),
                (0.0, 0.5, -1.0),
                (0.5, 0.0,  1.0),
                (0.5, 0.5,  1.0),
                (0.0, 0.5,  1.0),
                (0.0, 0.0,  0.0),
                (1.0, 0.0,  0.0),
                (0.0, 1.0,  0.0),
            ), dtype=Real)
        case ElementTypes.Volume20:
            return np.array((
                (-1.0, -1.0, -1.0),
                ( 1.0, -1.0, -1.0),
                ( 1.0,  1.0, -1.0),
                (-1.0,  1.0, -1.0),
                (-1.0, -1.0,  1.0),
                ( 1.0, -1.0,  1.0),
                ( 1.0,  1.0,  1.0),
                (-1.0,  1.0,  1.0),
                ( 0.0, -1.0, -1.0),
                ( 1.0,  0.0, -1.0),
                ( 0.0,  1.0, -1.0),
                (-1.0,  0.0, -1.0),
                ( 0.0, -1.0,  1.0),
                ( 1.0,  0.0,  1.0),
                ( 0.0,  1.0,  1.0),
                (-1.0,  0.0,  1.0),
                (-1.0, -1.0,  0.0),
                ( 1.0, -1.0,  0.0),
                ( 1.0,  1.0,  0.0),
                (-1.0,  1.0,  0.0),
            ), dtype=Real)

def integrationPoints(element: Element | Surface) -> tuple[RealMatrix, RealVector]:
    """
    Returns a matrix containing the natural coordinates of the integration points and a vector containing the
    corresponding weights. Some element types support a reduced integration scheme.
    """
    matrix: RealMatrix
    match element.type:
        case ElementTypes.Line2:
            matrix = np.array((
                (-0.5773502691896258, 0.0, 0.0, 1.0),
                ( 0.5773502691896258, 0.0, 0.0, 1.0),
            ), dtype=Real) if not element.section.reducedIntegration else np.array((
                (0.0, 0.0, 0.0, 2.0),
            ), dtype=Real)
        case ElementTypes.Line3:
            matrix = np.array((
                (-0.7745966692414834, 0.0, 0.0, 0.5555555555555556),
                ( 0.7745966692414834, 0.0, 0.0, 0.5555555555555556),
                ( 0.0000000000000000, 0.0, 0.0, 0.8888888888888889),
            ), dtype=Real) if not element.section.reducedIntegration else np.array((
                (-0.5773502691896258, 0.0, 0.0, 1.0),
                ( 0.5773502691896258, 0.0, 0.0, 1.0),
            ), dtype=Real)
        case ElementTypes.Plane3:
            matrix = np.array((
                (0.3333333333333333, 0.3333333333333333, 0.0, 0.5),
            ), dtype=Real)
        case ElementTypes.Plane4:
            matrix = np.array((
                (-0.5773502691896258, -0.5773502691896258, 0.0, 1.0),
                ( 0.5773502691896258, -0.5773502691896258, 0.0, 1.0),
                ( 0.5773502691896258,  0.5773502691896258, 0.0, 1.0),
                (-0.5773502691896258,  0.5773502691896258, 0.0, 1.0),
            ), dtype=Real) if not element.section.reducedIntegration else np.array((
                (0.0, 0.0, 0.0, 4.0),
            ), dtype=Real)
        case ElementTypes.Plane6:
            matrix = np.array((
                (0.1666666666666667, 0.1666666666666667, 0.0, 0.1666666666666667),
                (0.6666666666666667, 0.1666666666666667, 0.0, 0.1666666666666667),
                (0.1666666666666667, 0.6666666666666667, 0.0, 0.1666666666666667),
            ), dtype=Real)
        case ElementTypes.Plane8:
            matrix = np.array((
                (-0.7745966692414834, -0.7745966692414834, 0.0, 0.3086419753086420),
                ( 0.7745966692414834, -0.7745966692414834, 0.0, 0.3086419753086420),
                ( 0.7745966692414834,  0.7745966692414834, 0.0, 0.3086419753086420),
                (-0.7745966692414834,  0.7745966692414834, 0.0, 0.3086419753086420),
                ( 0.0000000000000000, -0.7745966692414834, 0.0, 0.4938271604938271),
                ( 0.7745966692414834,  0.0000000000000000, 0.0, 0.4938271604938271),
                ( 0.0000000000000000,  0.7745966692414834, 0.0, 0.4938271604938271),
                (-0.7745966692414834,  0.0000000000000000, 0.0, 0.4938271604938271),
                ( 0.0000000000000000,  0.0000000000000000, 0.0, 0.7901234567901234),
            ), dtype=Real) if not element.section.reducedIntegration else np.array((
                (-0.5773502691896258, -0.5773502691896258, 0.0, 1.0),
                ( 0.5773502691896258, -0.5773502691896258, 0.0, 1.0),
                ( 0.5773502691896258,  0.5773502691896258, 0.0, 1.0),
                (-0.5773502691896258,  0.5773502691896258, 0.0, 1.0),
            ), dtype=Real)
        case ElementTypes.Volume4:
            matrix = np.array((
                (0.25, 0.25, 0.25, 0.1666666666666667),
            ), dtype=Real)
        case ElementTypes.Volume6:
            matrix = np.array((
                (0.3333333333333333, 0.3333333333333333, -0.5773502691896258, 0.5),
                (0.3333333333333333, 0.3333333333333333,  0.5773502691896258, 0.5),
            ), dtype=Real)
        case ElementTypes.Volume8:
            matrix = np.array((
                (-0.5773502691896258, -0.5773502691896258, -0.5773502691896258, 1.0),
                ( 0.5773502691896258, -0.5773502691896258, -0.5773502691896258, 1.0),
                ( 0.5773502691896258,  0.5773502691896258, -0.5773502691896258, 1.0),
                (-0.5773502691896258,  0.5773502691896258, -0.5773502691896258, 1.0),
                (-0.5773502691896258, -0.5773502691896258,  0.5773502691896258, 1.0),
                ( 0.5773502691896258, -0.5773502691896258,  0.5773502691896258, 1.0),
                ( 0.5773502691896258,  0.5773502691896258,  0.5773502691896258, 1.0),
                (-0.5773502691896258,  0.5773502691896258,  0.5773502691896258, 1.0),
            ), dtype=Real) if not element.section.reducedIntegration else np.array((
                (0.0, 0.0, 0.0, 8.0),
            ), dtype=Real)
        case ElementTypes.Volume10:
            matrix = np.array((
                (0.1381966011250105, 0.1381966011250105, 0.1381966011250105, 0.0416666666666667),
                (0.5854101966249685, 0.1381966011250105, 0.1381966011250105, 0.0416666666666667),
                (0.1381966011250105, 0.5854101966249685, 0.1381966011250105, 0.0416666666666667),
                (0.1381966011250105, 0.1381966011250105, 0.5854101966249685, 0.0416666666666667),
            ), dtype=Real)
        case ElementTypes.Volume15:
            matrix = np.array((
                (0.1666666666666667, 0.1666666666666667, -0.7745966692414834, 0.0925925925925926),
                (0.6666666666666667, 0.1666666666666667, -0.7745966692414834, 0.0925925925925926),
                (0.1666666666666667, 0.6666666666666667, -0.7745966692414834, 0.0925925925925926),
                (0.1666666666666667, 0.1666666666666667,  0.7745966692414834, 0.0925925925925926),
                (0.6666666666666667, 0.1666666666666667,  0.7745966692414834, 0.0925925925925926),
                (0.1666666666666667, 0.6666666666666667,  0.7745966692414834, 0.0925925925925926),
                (0.1666666666666667, 0.1666666666666667,  0.0000000000000000, 0.1481481481481481),
                (0.6666666666666667, 0.1666666666666667,  0.0000000000000000, 0.1481481481481481),
                (0.1666666666666667, 0.6666666666666667,  0.0000000000000000, 0.1481481481481481),
            ), dtype=Real)
        case ElementTypes.Volume20:
            matrix = np.array((
                (-0.7745966692414834, -0.7745966692414834, -0.7745966692414834, 0.1714677640603567),
                ( 0.7745966692414834, -0.7745966692414834, -0.7745966692414834, 0.1714677640603567),
                ( 0.7745966692414834,  0.7745966692414834, -0.7745966692414834, 0.1714677640603567),
                (-0.7745966692414834,  0.7745966692414834, -0.7745966692414834, 0.1714677640603567),
                (-0.7745966692414834, -0.7745966692414834,  0.7745966692414834, 0.1714677640603567),
                ( 0.7745966692414834, -0.7745966692414834,  0.7745966692414834, 0.1714677640603567),
                ( 0.7745966692414834,  0.7745966692414834,  0.7745966692414834, 0.1714677640603567),
                (-0.7745966692414834,  0.7745966692414834,  0.7745966692414834, 0.1714677640603567),
                ( 0.0000000000000000, -0.7745966692414834, -0.7745966692414834, 0.2743484224965706),
                ( 0.7745966692414834,  0.0000000000000000, -0.7745966692414834, 0.2743484224965706),
                ( 0.0000000000000000,  0.7745966692414834, -0.7745966692414834, 0.2743484224965706),
                (-0.7745966692414834,  0.0000000000000000, -0.7745966692414834, 0.2743484224965706),
                ( 0.0000000000000000, -0.7745966692414834,  0.7745966692414834, 0.2743484224965706),
                ( 0.7745966692414834,  0.0000000000000000,  0.7745966692414834, 0.2743484224965706),
                ( 0.0000000000000000,  0.7745966692414834,  0.7745966692414834, 0.2743484224965706),
                (-0.7745966692414834,  0.0000000000000000,  0.7745966692414834, 0.2743484224965706),
                (-0.7745966692414834, -0.7745966692414834,  0.0000000000000000, 0.2743484224965706),
                ( 0.7745966692414834, -0.7745966692414834,  0.0000000000000000, 0.2743484224965706),
                ( 0.7745966692414834,  0.7745966692414834,  0.0000000000000000, 0.2743484224965706),
                (-0.7745966692414834,  0.7745966692414834,  0.0000000000000000, 0.2743484224965706),
                ( 0.0000000000000000, -0.7745966692414834,  0.0000000000000000, 0.4389574759945130),
                ( 0.7745966692414834,  0.0000000000000000,  0.0000000000000000, 0.4389574759945130),
                ( 0.0000000000000000,  0.7745966692414834,  0.0000000000000000, 0.4389574759945130),
                (-0.7745966692414834,  0.0000000000000000,  0.0000000000000000, 0.4389574759945130),
                ( 0.0000000000000000,  0.0000000000000000, -0.7745966692414834, 0.4389574759945130),
                ( 0.0000000000000000,  0.0000000000000000,  0.7745966692414834, 0.4389574759945130),
                ( 0.0000000000000000,  0.0000000000000000,  0.0000000000000000, 0.7023319615912208),
            ), dtype=Real) if not element.section.reducedIntegration else np.array((
                (-0.5773502691896258, -0.5773502691896258, -0.5773502691896258, 1.0),
                ( 0.5773502691896258, -0.5773502691896258, -0.5773502691896258, 1.0),
                ( 0.5773502691896258,  0.5773502691896258, -0.5773502691896258, 1.0),
                (-0.5773502691896258,  0.5773502691896258, -0.5773502691896258, 1.0),
                (-0.5773502691896258, -0.5773502691896258,  0.5773502691896258, 1.0),
                ( 0.5773502691896258, -0.5773502691896258,  0.5773502691896258, 1.0),
                ( 0.5773502691896258,  0.5773502691896258,  0.5773502691896258, 1.0),
                (-0.5773502691896258,  0.5773502691896258,  0.5773502691896258, 1.0),
            ), dtype=Real)
    return matrix[:, :3], matrix[:, 3]

def shapeFunctions(element: Element | Surface, r: float, s: float, t: float) -> RealVector:
    """Evaluates the element shape functions at the specified natural coordinates (usually an integration point)."""
    N: RealVector = np.zeros(shape=(element.nodeCount,), dtype=Real)
    match element.type:
        case ElementTypes.Line2:
            N[0] = 0.5*(1.0 - r)
            N[1] = 0.5*(1.0 + r)
        case ElementTypes.Line3:
            N[0] = 0.5*r*(r - 1.0)
            N[1] = 0.5*r*(r + 1.0)
            N[2] =       1.0 - r*r
        case ElementTypes.Plane3:
            N[0] = 1.0 - r - s
            N[1] =           r
            N[2] =           s
        case ElementTypes.Plane4:
            N[0] =  0.25*(r - 1.0)*(s - 1.0)
            N[1] = -0.25*(r + 1.0)*(s - 1.0)
            N[2] =  0.25*(r + 1.0)*(s + 1.0)
            N[3] = -0.25*(r - 1.0)*(s + 1.0)
        case ElementTypes.Plane6:
            N[0] = (2.0*r + 2.0*s - 1.0)*(r + s - 1.0)
            N[1] =                     r*(2.0*r - 1.0)
            N[2] =                     s*(2.0*s - 1.0)
            N[3] =                -4.0*r*(r + s - 1.0)
            N[4] =                             4.0*r*s
            N[5] =                -4.0*s*(r + s - 1.0)
        case ElementTypes.Plane8:
            N[0] = -0.25*(r - 1.0)*(s - 1.0)*(r + s + 1.0)
            N[1] = -0.25*(r + 1.0)*(s - 1.0)*(r - s - 1.0)
            N[2] =  0.25*(r + 1.0)*(s + 1.0)*(r + s - 1.0)
            N[3] =  0.25*(r - 1.0)*(s + 1.0)*(r - s + 1.0)
            N[4] =               0.5*(r*r - 1.0)*(s - 1.0)
            N[5] =              -0.5*(s*s - 1.0)*(r + 1.0)
            N[6] =              -0.5*(r*r - 1.0)*(s + 1.0)
            N[7] =               0.5*(s*s - 1.0)*(r - 1.0)
        case ElementTypes.Volume4:
            N[0] = 1.0 - r - s - t
            N[1] =               r
            N[2] =               s
            N[3] =               t
        case ElementTypes.Volume6:
            N[0] =  0.5*(t - 1.0)*(r + s - 1.0)
            N[1] =             -0.5*(t - 1.0)*r
            N[2] =             -0.5*(t - 1.0)*s
            N[3] = -0.5*(t + 1.0)*(r + s - 1.0)
            N[4] =              0.5*(t + 1.0)*r
            N[5] =              0.5*(t + 1.0)*s
        case ElementTypes.Volume8:
            N[0] = -0.125*(r - 1.0)*(s - 1.0)*(t - 1.0)
            N[1] =  0.125*(r + 1.0)*(s - 1.0)*(t - 1.0)
            N[2] = -0.125*(r + 1.0)*(s + 1.0)*(t - 1.0)
            N[3] =  0.125*(r - 1.0)*(s + 1.0)*(t - 1.0)
            N[4] =  0.125*(r - 1.0)*(s - 1.0)*(t + 1.0)
            N[5] = -0.125*(r + 1.0)*(s - 1.0)*(t + 1.0)
            N[6] =  0.125*(r + 1.0)*(s + 1.0)*(t + 1.0)
            N[7] = -0.125*(r - 1.0)*(s + 1.0)*(t + 1.0)
        case ElementTypes.Volume10:
            N[0] = (r + s + t - 1.0)*(2.0*r + 2.0*s + 2.0*t - 1.0)
            N[1] =                                 r*(2.0*r - 1.0)
            N[2] =                                 s*(2.0*s - 1.0)
            N[3] =                                 t*(2.0*t - 1.0)
            N[4] =                        -4.0*r*(r + s + t - 1.0)
            N[5] =                                         4.0*r*s
            N[6] =                        -4.0*s*(r + s + t - 1.0)
            N[7] =                        -4.0*t*(r + s + t - 1.0)
            N[8] =                                         4.0*r*t
            N[9] =                                         4.0*s*t
        case ElementTypes.Volume15:
            N[0]  = -0.5*(t - 1.0)*(r + s - 1.0)*(2.0*r + 2.0*s + t)
            N[1]  =                0.5*r*(t - 1.0)*(t - 2.0*r + 2.0)
            N[2]  =                0.5*s*(t - 1.0)*(t - 2.0*s + 2.0)
            N[3]  =  0.5*(t + 1.0)*(r + s - 1.0)*(2.0*r + 2.0*s - t)
            N[4]  =                0.5*r*(t + 1.0)*(2.0*r + t - 2.0)
            N[5]  =                0.5*s*(t + 1.0)*(2.0*s + t - 2.0)
            N[6]  =                    2.0*r*(t - 1.0)*(r + s - 1.0)
            N[7]  =                               -2.0*r*s*(t - 1.0)
            N[8]  =                    2.0*s*(t - 1.0)*(r + s - 1.0)
            N[9]  =                   -2.0*r*(t + 1.0)*(r + s - 1.0)
            N[10] =                                2.0*r*s*(t + 1.0)
            N[11] =                   -2.0*s*(t + 1.0)*(r + s - 1.0)
            N[12] =                        (t*t - 1.0)*(r + s - 1.0)
            N[13] =                                   -r*(t*t - 1.0)
            N[14] =                                   -s*(t*t - 1.0)
        case ElementTypes.Volume20:
            N[0]  =  0.125*(r - 1.0)*(s - 1.0)*(t - 1.0)*(r + s + t + 2.0)
            N[1]  =  0.125*(r + 1.0)*(s - 1.0)*(t - 1.0)*(r - s - t - 2.0)
            N[2]  = -0.125*(r + 1.0)*(s + 1.0)*(t - 1.0)*(r + s - t - 2.0)
            N[3]  = -0.125*(r - 1.0)*(s + 1.0)*(t - 1.0)*(r - s + t + 2.0)
            N[4]  = -0.125*(r - 1.0)*(s - 1.0)*(t + 1.0)*(r + s - t + 2.0)
            N[5]  = -0.125*(r + 1.0)*(s - 1.0)*(t + 1.0)*(r - s + t - 2.0)
            N[6]  =  0.125*(r + 1.0)*(s + 1.0)*(t + 1.0)*(r + s + t - 2.0)
            N[7]  =  0.125*(r - 1.0)*(s + 1.0)*(t + 1.0)*(r - s - t + 2.0)
            N[8]  =                  -0.25*(r*r - 1.0)*(s - 1.0)*(t - 1.0)
            N[9]  =                   0.25*(s*s - 1.0)*(r + 1.0)*(t - 1.0)
            N[10] =                   0.25*(r*r - 1.0)*(s + 1.0)*(t - 1.0)
            N[11] =                  -0.25*(s*s - 1.0)*(r - 1.0)*(t - 1.0)
            N[12] =                   0.25*(r*r - 1.0)*(s - 1.0)*(t + 1.0)
            N[13] =                  -0.25*(s*s - 1.0)*(r + 1.0)*(t + 1.0)
            N[14] =                  -0.25*(r*r - 1.0)*(s + 1.0)*(t + 1.0)
            N[15] =                   0.25*(s*s - 1.0)*(r - 1.0)*(t + 1.0)
            N[16] =                  -0.25*(t*t - 1.0)*(r - 1.0)*(s - 1.0)
            N[17] =                   0.25*(t*t - 1.0)*(r + 1.0)*(s - 1.0)
            N[18] =                  -0.25*(t*t - 1.0)*(r + 1.0)*(s + 1.0)
            N[19] =                   0.25*(t*t - 1.0)*(r - 1.0)*(s + 1.0)
    return N

def naturalDerivatives(element: Element | Surface, r: float, s: float, t: float) -> RealMatrix:
    """
    Evaluates the natural derivatives of the element shape functions at the given natural coordinates (usually an
    integration point).
    """
    Nr: RealMatrix = np.zeros(shape=(3, element.nodeCount), dtype=Real)
    match element.type:
        case ElementTypes.Line2:
            # ∂Ni/∂r
            Nr[0, 0] = -0.5
            Nr[0, 1] =  0.5
        case ElementTypes.Line3:
            # ∂Ni/∂r
            Nr[0, 0] = (r - 0.5)
            Nr[0, 1] = (r + 0.5)
            Nr[0, 2] =    -2.0*r
        case ElementTypes.Plane3:
            # ∂Ni/∂r
            Nr[0, 0] = -1.0
            Nr[0, 1] =  1.0
            Nr[0, 2] =  0.0
            # ∂Ni/∂s
            Nr[1, 0] = -1.0
            Nr[1, 1] =  0.0
            Nr[1, 2] =  1.0
        case ElementTypes.Plane4:
            # ∂Ni/∂r
            Nr[0, 0] =  0.25*(s - 1.0)
            Nr[0, 1] = -0.25*(s - 1.0)
            Nr[0, 2] =  0.25*(s + 1.0)
            Nr[0, 3] = -0.25*(s + 1.0)
            # ∂Ni/∂s
            Nr[1, 0] =  0.25*(r - 1.0)
            Nr[1, 1] = -0.25*(r + 1.0)
            Nr[1, 2] =  0.25*(r + 1.0)
            Nr[1, 3] = -0.25*(r - 1.0)
        case ElementTypes.Plane6:
            # ∂Ni/∂r
            Nr[0, 0] = 4.0*r + 4.0*s - 3.0
            Nr[0, 1] =         4.0*r - 1.0
            Nr[0, 2] =                 0.0
            Nr[0, 3] = 4.0 - 8.0*r - 4.0*s
            Nr[0, 4] =               4.0*s
            Nr[0, 5] =              -4.0*s
            # ∂Ni/∂s
            Nr[1, 0] = 4.0*r + 4.0*s - 3.0
            Nr[1, 1] =                 0.0
            Nr[1, 2] =         4.0*s - 1.0
            Nr[1, 3] =              -4.0*r
            Nr[1, 4] =               4.0*r
            Nr[1, 5] = 4.0 - 8.0*s - 4.0*r
        case ElementTypes.Plane8:
            # ∂Ni/∂r
            Nr[0, 0] = -0.25*(2.0*r + s)*(s - 1.0)
            Nr[0, 1] = -0.25*(2.0*r - s)*(s - 1.0)
            Nr[0, 2] =  0.25*(2.0*r + s)*(s + 1.0)
            Nr[0, 3] =  0.25*(2.0*r - s)*(s + 1.0)
            Nr[0, 4] =                 r*(s - 1.0)
            Nr[0, 5] =            -0.5*(s*s - 1.0)
            Nr[0, 6] =                -r*(s + 1.0)
            Nr[0, 7] =             0.5*(s*s - 1.0)
            # ∂Ni/∂s
            Nr[1, 0] = -0.25*(r + 2.0*s)*(r - 1.0)
            Nr[1, 1] = -0.25*(r - 2.0*s)*(r + 1.0)
            Nr[1, 2] =  0.25*(r + 2.0*s)*(r + 1.0)
            Nr[1, 3] =  0.25*(r - 2.0*s)*(r - 1.0)
            Nr[1, 4] =             0.5*(r*r - 1.0)
            Nr[1, 5] =                -s*(r + 1.0)
            Nr[1, 6] =            -0.5*(r*r - 1.0)
            Nr[1, 7] =                 s*(r - 1.0)
        case ElementTypes.Volume4:
            # ∂Ni/∂r
            Nr[0, 0] = -1.0
            Nr[0, 1] =  1.0
            Nr[0, 2] =  0.0
            Nr[0, 3] =  0.0
            # ∂Ni/∂s
            Nr[1, 0] = -1.0
            Nr[1, 1] =  0.0
            Nr[1, 2] =  1.0
            Nr[1, 3] =  0.0
            # ∂Ni/∂t
            Nr[2, 0] = -1.0
            Nr[2, 1] =  0.0
            Nr[2, 2] =  0.0
            Nr[2, 3] =  1.0
        case ElementTypes.Volume6:
            # ∂Ni/∂r
            Nr[0, 0] =  0.5*(t - 1.0)
            Nr[0, 1] = -0.5*(t - 1.0)
            Nr[0, 2] =            0.0
            Nr[0, 3] = -0.5*(t + 1.0)
            Nr[0, 4] =  0.5*(t + 1.0)
            Nr[0, 5] =            0.0
            # ∂Ni/∂s
            Nr[1, 0] =  0.5*(t - 1.0)
            Nr[1, 1] =            0.0
            Nr[1, 2] = -0.5*(t - 1.0)
            Nr[1, 3] = -0.5*(t + 1.0)
            Nr[1, 4] =            0.0
            Nr[1, 5] =  0.5*(t + 1.0)
            # ∂Ni/∂t
            Nr[2, 0] =  0.5*(r + s - 1.0)
            Nr[2, 1] =             -0.5*r
            Nr[2, 2] =             -0.5*s
            Nr[2, 3] = -0.5*(r + s - 1.0)
            Nr[2, 4] =              0.5*r
            Nr[2, 5] =              0.5*s
        case ElementTypes.Volume8:
            # ∂Ni/∂r
            Nr[0, 0] = -0.125*(s - 1.0)*(t - 1.0)
            Nr[0, 1] =  0.125*(s - 1.0)*(t - 1.0)
            Nr[0, 2] = -0.125*(s + 1.0)*(t - 1.0)
            Nr[0, 3] =  0.125*(s + 1.0)*(t - 1.0)
            Nr[0, 4] =  0.125*(s - 1.0)*(t + 1.0)
            Nr[0, 5] = -0.125*(s - 1.0)*(t + 1.0)
            Nr[0, 6] =  0.125*(s + 1.0)*(t + 1.0)
            Nr[0, 7] = -0.125*(s + 1.0)*(t + 1.0)
            # ∂Ni/∂s
            Nr[1, 0] = -0.125*(r - 1.0)*(t - 1.0)
            Nr[1, 1] =  0.125*(r + 1.0)*(t - 1.0)
            Nr[1, 2] = -0.125*(r + 1.0)*(t - 1.0)
            Nr[1, 3] =  0.125*(r - 1.0)*(t - 1.0)
            Nr[1, 4] =  0.125*(r - 1.0)*(t + 1.0)
            Nr[1, 5] = -0.125*(r + 1.0)*(t + 1.0)
            Nr[1, 6] =  0.125*(r + 1.0)*(t + 1.0)
            Nr[1, 7] = -0.125*(r - 1.0)*(t + 1.0)
            # ∂Ni/∂t
            Nr[2, 0] = -0.125*(r - 1.0)*(s - 1.0)
            Nr[2, 1] =  0.125*(r + 1.0)*(s - 1.0)
            Nr[2, 2] = -0.125*(r + 1.0)*(s + 1.0)
            Nr[2, 3] =  0.125*(r - 1.0)*(s + 1.0)
            Nr[2, 4] =  0.125*(r - 1.0)*(s - 1.0)
            Nr[2, 5] = -0.125*(r + 1.0)*(s - 1.0)
            Nr[2, 6] =  0.125*(r + 1.0)*(s + 1.0)
            Nr[2, 7] = -0.125*(r - 1.0)*(s + 1.0)
        case ElementTypes.Volume10:
            # ∂Ni/∂r
            Nr[0, 0] = 4.0*r + 4.0*s + 4.0*t - 3.0
            Nr[0, 1] =                 4.0*r - 1.0
            Nr[0, 2] =                         0.0
            Nr[0, 3] =                         0.0
            Nr[0, 4] = 4.0 - 8.0*r - 4.0*s - 4.0*t
            Nr[0, 5] =                       4.0*s
            Nr[0, 6] =                      -4.0*s
            Nr[0, 7] =                      -4.0*t
            Nr[0, 8] =                       4.0*t
            Nr[0, 9] =                         0.0
            # ∂Ni/∂s
            Nr[1, 0] = 4.0*r + 4.0*s + 4.0*t - 3.0
            Nr[1, 1] =                         0.0
            Nr[1, 2] =                 4.0*s - 1.0
            Nr[1, 3] =                         0.0
            Nr[1, 4] =                      -4.0*r
            Nr[1, 5] =                       4.0*r
            Nr[1, 6] = 4.0 - 4.0*r - 8.0*s - 4.0*t
            Nr[1, 7] =                      -4.0*t
            Nr[1, 8] =                         0.0
            Nr[1, 9] =                       4.0*t
            # ∂Ni/∂t
            Nr[2, 0] = 4.0*r + 4.0*s + 4.0*t - 3.0
            Nr[2, 1] =                         0.0
            Nr[2, 2] =                         0.0
            Nr[2, 3] =                 4.0*t - 1.0
            Nr[2, 4] =                      -4.0*r
            Nr[2, 5] =                         0.0
            Nr[2, 6] =                      -4.0*s
            Nr[2, 7] = 4.0 - 4.0*r - 4.0*s - 8.0*t
            Nr[2, 8] =                       4.0*r
            Nr[2, 9] =                       4.0*s
        case ElementTypes.Volume15:
            # ∂Ni/∂r
            Nr[0,  0] = -0.5*(t - 1.0)*(4.0*r + 4.0*s + t - 2.0)
            Nr[0,  1] =          0.5*(t - 1.0)*(t - 4.0*r + 2.0)
            Nr[0,  2] =                                      0.0
            Nr[0,  3] =  0.5*(t + 1.0)*(4.0*r + 4.0*s - t - 2.0)
            Nr[0,  4] =          0.5*(t + 1.0)*(4.0*r + t - 2.0)
            Nr[0,  5] =                                      0.0
            Nr[0,  6] =          2.0*(t - 1.0)*(2.0*r + s - 1.0)
            Nr[0,  7] =                         -2.0*s*(t - 1.0)
            Nr[0,  8] =                          2.0*s*(t - 1.0)
            Nr[0,  9] =         -2.0*(t + 1.0)*(2.0*r + s - 1.0)
            Nr[0, 10] =                          2.0*s*(t + 1.0)
            Nr[0, 11] =                         -2.0*s*(t + 1.0)
            Nr[0, 12] =                                t*t - 1.0
            Nr[0, 13] =                                1.0 - t*t
            Nr[0, 14] =                                      0.0
            # ∂Ni/∂s
            Nr[1,  0] = -0.5*(t - 1.0)*(4.0*r + 4.0*s + t - 2.0)
            Nr[1,  1] =                                      0.0
            Nr[1,  2] =          0.5*(t - 1.0)*(t - 4.0*s + 2.0)
            Nr[1,  3] =  0.5*(t + 1.0)*(4.0*r + 4.0*s - t - 2.0)
            Nr[1,  4] =                                      0.0
            Nr[1,  5] =          0.5*(t + 1.0)*(4.0*s + t - 2.0)
            Nr[1,  6] =                          2.0*r*(t - 1.0)
            Nr[1,  7] =                         -2.0*r*(t - 1.0)
            Nr[1,  8] =          2.0*(t - 1.0)*(r + 2.0*s - 1.0)
            Nr[1,  9] =                         -2.0*r*(t + 1.0)
            Nr[1, 10] =                          2.0*r*(t + 1.0)
            Nr[1, 11] =         -2.0*(t + 1.0)*(r + 2.0*s - 1.0)
            Nr[1, 12] =                                t*t - 1.0
            Nr[1, 13] =                                      0.0
            Nr[1, 14] =                                1.0 - t*t
            # ∂Ni/∂t
            Nr[2,  0] = -0.5*(r + s - 1.0)*(2.0*r + 2.0*s + 2.0*t - 1.0)
            Nr[2,  1] =                      0.5*r*(2.0*t - 2.0*r + 1.0)
            Nr[2,  2] =                      0.5*s*(2.0*t - 2.0*s + 1.0)
            Nr[2,  3] =  0.5*(r + s - 1.0)*(2.0*r + 2.0*s - 2.0*t - 1.0)
            Nr[2,  4] =                      0.5*r*(2.0*r + 2.0*t - 1.0)
            Nr[2,  5] =                      0.5*s*(2.0*s + 2.0*t - 1.0)
            Nr[2,  6] =                              2.0*r*(r + s - 1.0)
            Nr[2,  7] =                                         -2.0*r*s
            Nr[2,  8] =                              2.0*s*(r + s - 1.0)
            Nr[2,  9] =                             -2.0*r*(r + s - 1.0)
            Nr[2, 10] =                                          2.0*r*s
            Nr[2, 11] =                             -2.0*s*(r + s - 1.0)
            Nr[2, 12] =                              2.0*t*(r + s - 1.0)
            Nr[2, 13] =                                         -2.0*r*t
            Nr[2, 14] =                                         -2.0*s*t
        case ElementTypes.Volume20:
            # ∂Ni/∂r
            Nr[0,  0] =  0.125*(s - 1.0)*(t - 1.0)*(2.0*r + s + t + 1.0)
            Nr[0,  1] =  0.125*(s - 1.0)*(t - 1.0)*(2.0*r - s - t - 1.0)
            Nr[0,  2] = -0.125*(s + 1.0)*(t - 1.0)*(2.0*r + s - t - 1.0)
            Nr[0,  3] = -0.125*(s + 1.0)*(t - 1.0)*(2.0*r - s + t + 1.0)
            Nr[0,  4] = -0.125*(s - 1.0)*(t + 1.0)*(2.0*r + s - t + 1.0)
            Nr[0,  5] = -0.125*(s - 1.0)*(t + 1.0)*(2.0*r - s + t - 1.0)
            Nr[0,  6] =  0.125*(s + 1.0)*(t + 1.0)*(2.0*r + s + t - 1.0)
            Nr[0,  7] =  0.125*(s + 1.0)*(t + 1.0)*(2.0*r - s - t + 1.0)
            Nr[0,  8] =                      -0.50*r*(s - 1.0)*(t - 1.0)
            Nr[0,  9] =                       0.25*(s*s - 1.0)*(t - 1.0)
            Nr[0, 10] =                       0.50*r*(s + 1.0)*(t - 1.0)
            Nr[0, 11] =                      -0.25*(s*s - 1.0)*(t - 1.0)
            Nr[0, 12] =                       0.50*r*(s - 1.0)*(t + 1.0)
            Nr[0, 13] =                      -0.25*(s*s - 1.0)*(t + 1.0)
            Nr[0, 14] =                      -0.50*r*(s + 1.0)*(t + 1.0)
            Nr[0, 15] =                       0.25*(s*s - 1.0)*(t + 1.0)
            Nr[0, 16] =                      -0.25*(t*t - 1.0)*(s - 1.0)
            Nr[0, 17] =                       0.25*(t*t - 1.0)*(s - 1.0)
            Nr[0, 18] =                      -0.25*(t*t - 1.0)*(s + 1.0)
            Nr[0, 19] =                       0.25*(t*t - 1.0)*(s + 1.0)
            # ∂Ni/∂s
            Nr[1,  0] =  0.125*(r - 1.0)*(t - 1.0)*(r + 2.0*s + t + 1.0)
            Nr[1,  1] =  0.125*(r + 1.0)*(t - 1.0)*(r - 2.0*s - t - 1.0)
            Nr[1,  2] = -0.125*(r + 1.0)*(t - 1.0)*(r + 2.0*s - t - 1.0)
            Nr[1,  3] = -0.125*(r - 1.0)*(t - 1.0)*(r - 2.0*s + t + 1.0)
            Nr[1,  4] = -0.125*(r - 1.0)*(t + 1.0)*(r + 2.0*s - t + 1.0)
            Nr[1,  5] = -0.125*(r + 1.0)*(t + 1.0)*(r - 2.0*s + t - 1.0)
            Nr[1,  6] =  0.125*(r + 1.0)*(t + 1.0)*(r + 2.0*s + t - 1.0)
            Nr[1,  7] =  0.125*(r - 1.0)*(t + 1.0)*(r - 2.0*s - t + 1.0)
            Nr[1,  8] =                      -0.25*(r*r - 1.0)*(t - 1.0)
            Nr[1,  9] =                       0.50*s*(r + 1.0)*(t - 1.0)
            Nr[1, 10] =                       0.25*(r*r - 1.0)*(t - 1.0)
            Nr[1, 11] =                      -0.50*s*(r - 1.0)*(t - 1.0)
            Nr[1, 12] =                       0.25*(r*r - 1.0)*(t + 1.0)
            Nr[1, 13] =                      -0.50*s*(r + 1.0)*(t + 1.0)
            Nr[1, 14] =                      -0.25*(r*r - 1.0)*(t + 1.0)
            Nr[1, 15] =                       0.50*s*(r - 1.0)*(t + 1.0)
            Nr[1, 16] =                      -0.25*(t*t - 1.0)*(r - 1.0)
            Nr[1, 17] =                       0.25*(t*t - 1.0)*(r + 1.0)
            Nr[1, 18] =                      -0.25*(t*t - 1.0)*(r + 1.0)
            Nr[1, 19] =                       0.25*(t*t - 1.0)*(r - 1.0)
            # ∂Ni/∂t
            Nr[2,  0] =  0.125*(r - 1.0)*(s - 1.0)*(r + s + 2.0*t + 1.0)
            Nr[2,  1] =  0.125*(r + 1.0)*(s - 1.0)*(r - s - 2.0*t - 1.0)
            Nr[2,  2] = -0.125*(r + 1.0)*(s + 1.0)*(r + s - 2.0*t - 1.0)
            Nr[2,  3] = -0.125*(r - 1.0)*(s + 1.0)*(r - s + 2.0*t + 1.0)
            Nr[2,  4] = -0.125*(r - 1.0)*(s - 1.0)*(r + s - 2.0*t + 1.0)
            Nr[2,  5] = -0.125*(r + 1.0)*(s - 1.0)*(r - s + 2.0*t - 1.0)
            Nr[2,  6] =  0.125*(r + 1.0)*(s + 1.0)*(r + s + 2.0*t - 1.0)
            Nr[2,  7] =  0.125*(r - 1.0)*(s + 1.0)*(r - s - 2.0*t + 1.0)
            Nr[2,  8] =                      -0.25*(r*r - 1.0)*(s - 1.0)
            Nr[2,  9] =                       0.25*(s*s - 1.0)*(r + 1.0)
            Nr[2, 10] =                       0.25*(r*r - 1.0)*(s + 1.0)
            Nr[2, 11] =                      -0.25*(s*s - 1.0)*(r - 1.0)
            Nr[2, 12] =                       0.25*(r*r - 1.0)*(s - 1.0)
            Nr[2, 13] =                      -0.25*(s*s - 1.0)*(r + 1.0)
            Nr[2, 14] =                      -0.25*(r*r - 1.0)*(s + 1.0)
            Nr[2, 15] =                       0.25*(s*s - 1.0)*(r - 1.0)
            Nr[2, 16] =                      -0.50*t*(r - 1.0)*(s - 1.0)
            Nr[2, 17] =                       0.50*t*(r + 1.0)*(s - 1.0)
            Nr[2, 18] =                      -0.50*t*(r + 1.0)*(s + 1.0)
            Nr[2, 19] =                       0.50*t*(r - 1.0)*(s + 1.0)
    return Nr

def extrapolationApproach(element: Element | Surface) -> \
    Literal["constant", "linear in r", "linear in t", "bilinear in r, s", "trilinear in r, s, t"]:
    """Returns the extrapolation technique as a string for the specified element."""
    match element.type:
        case ElementTypes.Line2:
            return "linear in r" if not element.section.reducedIntegration else "constant"
        case ElementTypes.Line3:
            return "linear in r"
        case ElementTypes.Plane3:
            return "constant"
        case ElementTypes.Plane4:
            return "bilinear in r, s" if not element.section.reducedIntegration else "constant"
        case ElementTypes.Plane6:
            return "bilinear in r, s"
        case ElementTypes.Plane8:
            return "bilinear in r, s"
        case ElementTypes.Volume4:
            return "constant"
        case ElementTypes.Volume6:
            return "linear in t"
        case ElementTypes.Volume8:
            return "trilinear in r, s, t" if not element.section.reducedIntegration else "constant"
        case ElementTypes.Volume10:
            return "trilinear in r, s, t"
        case ElementTypes.Volume15:
            return "trilinear in r, s, t"
        case ElementTypes.Volume20:
            return "trilinear in r, s, t"

def evaluateElement(element: Element, X: RealMatrix, intPt: RealVector, weight: float) -> \
    tuple[RealVector, RealVector, RealMatrix, float]:
    """
    Returns the following items evaluated at the specified integration point:
    1. The physical coordinates (x, y, z).
    2. The shape functions.
    3. The derivatives of the shape functions.
    4. The integration point volume.
    """
    # modeling space
    k: int = element.modelingSpace.value

    # evaluate shape functions and their natural derivatives at the specified integration point
    N: RealVector = shapeFunctions(element, intPt[0], intPt[1], intPt[2])
    Nr: RealMatrix = naturalDerivatives(element, intPt[0], intPt[1], intPt[2])

    # compute physical coordinates of the integration point
    coord: RealVector = np.matmul(N, X)

    # compute the Jacobian
    J: RealMatrix = np.matmul(Nr[:k, :], X[:, :k])
    invJ, detJ = linalg.inverse(J)

    # compute physical derivatives of the shape functions
    Nx: RealMatrix = np.zeros(shape=Nr.shape, dtype=Real)
    Nx[:k, :] = np.matmul(invJ, Nr[:k, :])

    # integration point volume
    vol: float
    match element.section.type:
        case SectionTypes.PlaneStress | SectionTypes.PlaneStrain:
            vol = weight*abs(detJ)*element.section.thickness
        case SectionTypes.Axisymmetric:
            vol = weight*abs(detJ)*2.0*np.pi*coord[0]
        case SectionTypes.General:
            vol = weight*abs(detJ)

    # done
    return coord, N, Nx, vol

def evaluateSurface(surface: Surface, X: RealMatrix, intPt: RealVector, weight: float) -> \
    tuple[RealVector, RealVector, RealVector, float]:
    """
    Returns the following items evaluated at the specified integration point:
    1. The physical coordinates (x, y, z).
    2. The shape functions.
    3. The surface normal.
    4. The integration point area.
    """
    # modeling space
    k: int = surface.modelingSpace.value

    # evaluate shape functions and their natural derivatives at the specified integration point
    N: RealVector = shapeFunctions(surface, intPt[0], intPt[1], intPt[2])
    Nr: RealMatrix = naturalDerivatives(surface, intPt[0], intPt[1], intPt[2])

    # compute physical coordinates of the integration point
    coord: RealVector = np.matmul(N, X)

    # compute the Jacobian matrix
    J: RealMatrix = np.matmul(Nr[:k, :], X[:, :k+1])

    # compute surface normal
    n: RealVector
    match surface.modelingSpace:
        case ModelingSpaces.OneDimensional:
            n = np.array((J[0, 1], -J[0, 0], 0.0), dtype=Real)
        case ModelingSpaces.TwoDimensional:
            n = np.array((
                (J[0, 1]*J[1, 2] - J[0, 2]*J[1, 1]),
                (J[0, 2]*J[1, 0] - J[0, 0]*J[1, 2]),
                (J[0, 0]*J[1, 1] - J[0, 1]*J[1, 0]),
            ), dtype=Real)
        case ModelingSpaces.ThreeDimensional:
            raise NotImplementedError("3D surface in 4D space")
    detJ: float = np.sqrt(n[0]*n[0] + n[1]*n[1] + n[2]*n[2])
    n /= detJ

    # integration point area
    area: float
    match surface.section.type:
        case SectionTypes.PlaneStress | SectionTypes.PlaneStrain:
            area = weight*abs(detJ)*surface.section.thickness
        case SectionTypes.Axisymmetric:
            area = weight*abs(detJ)*2.0*np.pi*coord[0]
        case SectionTypes.General:
            area = weight*abs(detJ)

    # done
    return coord, N, n, area
