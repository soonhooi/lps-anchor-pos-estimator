from compactionmatrix import compactionmatrix
from numpy import concatenate
from numpy import linalg
from numpy import ones
from numpy import where
from numpy import zeros
from numpy.core.umath import isfinite
from numpy.random import random
from setdiff import setdiff


class structtype():
    pass


def tm_ransac_more_rows(d, sol, sys):
    r_c = d.shape
    d2 = d ** 2
    m = r_c[0]

    tryrows = setdiff(range(0, m), sol.rows)
    cr, dr = compactionmatrix(len(sol.cols))
    u, s, vh = linalg.svd(sol.Bhat[2:, 2:])
    v = vh.T
    v = (v[:, 0:2]).conj().T

    for ii in tryrows:

        d2n = d2[ii - 1, sol.cols - 1]

        maxnrinl = 0

        for kk in range(1, sys.ransac_k2 + 1):

            okcols = ((isfinite(d2n)).astype(int)).nonzero()
            tmp = random.permutation(len(okcols))

            if len(tmp) >= 4:

                trycols1 = okcols[tmp[0:3]]

                zz = sol.Bhat[0, :] * linalg.inv(dr.conj().T)
                ZZ_con1 = concatenate((zeros(3, 1), v), 1)
                ZZ = concatenate((ones(1, len(sol.cols)), ZZ_con1))
                ZZ0_1 = concatenate((1, zeros(1, len(sol.cols) - 1)), 1)
                ZZ0_2 = concatenate((zeros(3, 1), v), 1)
                ZZ0 = concatenate((ZZ0_1, ZZ0_2))

                xx = (d2n[0, trycols1] - zz[0, trycols1]) * linalg.inv(
                    ZZ[:, trycols1])

                a = (zz[okcols] + xx * ZZ[:, okcols])
                b = d2n[okcols]
                inlids = where(abs(b - a) < sys.ransac_threshold2)

                if len(inlids) > maxnrinl:
                    maxnrinl = len(inlids)
                    tmpsol = structtype()
                    tmpsol.row = ii
                    tmpsol.cols = sol.cols[trycols1]
                    tmpsol.Bhatn = xx * ZZ0
                    tmpsol.inlcols = sol.cols[okcols[inlids]]

        if maxnrinl > sys.min_inliers2:
            sol.rows = concatenate((sol.rows, tmpsol.row), 1)
            sol.inlmatrix[tmpsol.row, tmpsol.inlcols] = ones(
                1, len(tmpsol.inlcols))
            sol.Bhat = concatenate((sol.Bhat, tmpsol.Bhatn))
            sol.dl = compactionmatrix(len(sol.rows))

    return sol
