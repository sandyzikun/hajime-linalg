import cmath as cm

class Constants(object):
    NUM_TYPE = [ int, float, complex ]
    ITER_TYPE = [ list, tuple ]
    class VectorType(object):
        ALL_TYPE = [ "c", "col", "r", "row" ]
        COL_TYPE = [ "c", "col" ]
        ROW_TYPE = [ "r", "row" ]

def ismatrix(matrix):
    if type(matrix) not in Constants.ITER_TYPE:
        return False
    for i in range(len(matrix)):
        if type(matrix[i]) not in Constants.ITER_TYPE:
            return False
        if i and len(matrix[i]) != len(matrix[i - 1]):
            return False
        for j in range(len(matrix[i])):
            if type(matrix[i][j]) not in Constants.NUM_TYPE:
                return False
    return True

def index2range(idx, shp):
    if idx == None:
        start = 0
        stop = shp
        step = 1
    elif type(idx) == int:
        start = idx if idx >= 0 else shp - idx
        stop = start + 1
        step = 1
    elif type(idx) == slice:
        step = 1 if idx.step == None else idx.step
        if step > 0:
            start = 0 if idx.start == None else idx.start
            stop = shp if idx.stop == None else idx.stop
        elif step < 0:
            start = shp - 1 if idx.start == None else idx.start
            stop = -1 if idx.stop == None else idx.stop
    else:
        raise AssertionError
    return range(start, stop, step)

class Matrix(object):

    def __init__(self, data):
        assert ismatrix(data)
        self.__data = data
        self.__all = []
        for i in range(len(data)):
            for j in range(len(data[0])):
                self.__all.append(data[i][j])

    @property
    def data(self):
        return self.__data

    @property
    def copy(self):
        return Matrix(self.data)

    @property
    def shape(self):
        return (len(self.data), len(self.data[0]))

    @property
    def issquare(self):
        return self.shape[0] == self.shape[1]

    def __repr__(self):
        longest = self.data[0][0]
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if len(str(self.data[i][j])) > len(str(longest)):
                    longest = self.data[i][j]
        longest = len(str(longest))
        return "Matrix[\n" + "\n".join([ (" " + " ".join([ (" " * (longest - len(str(self.data[i][j])))) + str(self.data[i][j]) for j in range(self.shape[1]) ])) for i in range(self.shape[0]) ]) + "\n]"

    def __getitem__(self, idx):
        if type(idx) == tuple and len(idx) == 2:
            return Matrix([ [ self.data[i][j] for j in index2range(idx[1], self.shape[1]) ] for i in index2range(idx[0], self.shape[0]) ])
        else:
            return Matrix([ [ self.data[i][j] for j in index2range(None, self.shape[1]) ] for i in index2range(idx, self.shape[0]) ])

    def __len__(self):
        return self.shape[0] * self.shape[1]

    def __pos__(self):
        return Matrix(self.data)

    def __neg__(self):
        return Matrix([ [ -self.data[i][j] for j in range(self.shape[1]) ] for i in range(self.shape[0]) ])

    def __abs__(self):
        return Matrix([ [ abs(self.data[i][j]) for j in range(self.shape[1]) ] for i in range(self.shape[0]) ])

    def __add__(self, other):
        assert self.shape == other.shape
        return Matrix([ [ (self.data[i][j] + other.data[i][j]) for j in range(self.shape[1]) ] for i in range(self.shape[0]) ])

    def __sub__(self, other):
        assert self.shape == other.shape
        return Matrix([ [ (self.data[i][j] - other.data[i][j]) for j in range(self.shape[1]) ] for i in range(self.shape[0]) ])

    def __matmul__(self, other):
        assert self.shape[1] == other.shape[0]
        return Matrix([ [ sum([ (self.data[i][k] * other.data[k][j]) for k in range(self.shape[1]) ]) for j in range(other.shape[1]) ] for i in range(self.shape[0]) ])

    def __mul__(self, other):
        if type(other) in Constants.NUM_TYPE:
            assert type(other) in Constants.NUM_TYPE
            return Matrix([ [ (self.data[i][j] * other) for j in range(self.shape[1]) ] for i in range(self.shape[0]) ])
        elif type(other) == Matrix:
            return self @ other
        else:
            raise AssertionError

    def __pow__(self, other):
        assert self.issquare and type(other) == int and other >= 0
        if other:
            return self if other == 1 else self @ self.__pow__(other - 1)
        else:
            return identity(self.shape[0])

    def __truediv__(self, other):
        if type(other) in Constants.NUM_TYPE:
            return Matrix([ [ (self.data[i][j] / other) for j in range(self.shape[1]) ] for i in range(self.shape[0]) ])
        elif type(other) == Matrix:
            return Matrix(self.data) @ other.inverse
        else:
            raise AssertionError

    def __floordiv__(self, other):
        assert type(other) in Constants.NUM_TYPE
        return Matrix([ [ (self.data[i][j] // other) for j in range(self.shape[1]) ] for i in range(self.shape[0]) ])

    def __mod__(self, other):
        assert type(other) in Constants.NUM_TYPE
        return Matrix([ [ (self.data[i][j] % other) for j in range(self.shape[1]) ] for i in range(self.shape[0]) ])

    @property
    def transposition(self):
        return Matrix([ [ self.__data[j][i] for j in range(len(self.__data)) ] for i in range(len(self.__data[0])) ])

    def __near_zeros(self, idx, drct):
        assert self.issquare and type(drct) == str and drct.lower() in [ "r", "l" ]
        shp = self.shape[0]
        if drct.lower() == "r":
            for i in range(idx + 1):
                for j in range(idx + 1, shp):
                    if self.data[i][j] != 0:
                        return False
            return True
        elif drct.lower() == "l":
            for i in range(idx + 1, shp):
                for j in range(idx + 1):
                    if self.data[i][j] != 0:
                        return False
            return True

    @property
    def determinant(self):
        assert self.issquare
        shp = self.shape[0]
        if shp == 1:
            return self.data[0][0]
        elif shp == 2:
            return self.data[0][0] * self.data[1][1] - self.data[0][1] * self.data[1][0]
        elif shp == 3:
            return self.data[0][0] * self.data[1][1] * self.data[2][2] \
                + self.data[0][1] * self.data[1][2] * self.data[2][0] \
                + self.data[0][2] * self.data[1][0] * self.data[2][1] \
                - self.data[0][2] * self.data[1][1] * self.data[2][0] \
                - self.data[0][1] * self.data[1][0] * self.data[2][2] \
                - self.data[0][0] * self.data[1][2] * self.data[2][1]
        else:
            # TODO: FIXME! MDZZ
            """
            for idx in range(shp):
                if self.__near_zeros(idx, "r") or self.__near_zeros(idx, "l"):
                    print(self[ : idx + 1 , : idx + 1 ], self[ idx + 1 : , idx + 1 : ], sep = "")
                    return self[ : idx + 1 , : idx + 1 ].determinant * self[ idx + 1 : , idx + 1 : ].determinant
            """
            return sum([ (self.data[i][0] * self.alg_cofactor(i, 0)) for i in range(self.shape[0]) ])

    def comatrix(self, i, j):
        assert self.issquare
        shp = self.shape[0]
        assert i >= 0 and i < shp
        assert j >= 0 and j < shp
        mtrx = []
        for _i in range(shp):
            if _i == i:
                continue
            mtrx.append([])
            for _j in range(shp):
                if _j == j:
                    continue
                mtrx[-1].append(self.data[_i][_j])
        return Matrix(mtrx)

    def cofactor(self, i, j):
        return self.comatrix(i, j).determinant

    def alg_cofactor(self, i, j):
        return -self.cofactor(i, j) if (i + j) % 2 else self.cofactor(i, j)

    @property
    def adjugate(self):
        assert self.determinant
        return Matrix([ [ self.alg_cofactor(j, i) for j in range(self.shape[1]) ] for i in range(self.shape[0]) ])

    @property
    def inverse(self):
        return self.adjugate / self.determinant

    def std_xchg(self, typ, i, j):
        assert type(typ) == str and typ.lower() in Constants.VectorType.ALL_TYPE
        if typ.lower() in Constants.VectorType.ROW_TYPE:
            assert 0 <= i < self.shape[0] and 0 <= j < self.shape[0] and i != j
            newmat = []
            for _i in range(self.shape[0]):
                newmat.append([])
                for _j in range(self.shape[1]):
                    if _i == i:
                        newmat[-1].append(self.data[j][_j])
                    elif _i == j:
                        newmat[-1].append(self.data[i][_j])
                    else:
                        newmat[-1].append(self.data[_i][_j])
            return Matrix(newmat)
        elif typ.lower() in Constants.VectorType.COL_TYPE:
            assert 0 <= i < self.shape[1] and 0 <= j < self.shape[1] and i != j
            newmat = []
            for _i in range(self.shape[0]):
                newmat.append([])
                for _j in range(self.shape[1]):
                    if _j == i:
                        newmat[-1].append(self.data[_i][j])
                    elif _j == j:
                        newmat[-1].append(self.data[_i][i])
                    else:
                        newmat.append(self.data[_i][_j])
            return Matrix(newmat)

    def std_mtpl(self, typ, idx, times):
        assert type(typ) == str and typ.lower() in Constants.VectorType.ALL_TYPE and times
        if typ.lower() in Constants.VectorType.ROW_TYPE:
            assert 0 <= idx < self.shape[0]
            newmat = []
            for _i in range(self.shape[0]):
                newmat.append([])
                for _j in range(self.shape[1]):
                    newmat[-1].append(self.data[_i][_j] if _i != idx else (self.data[_i][_j] * times))
            return Matrix(newmat)
        elif typ.lower() in Constants.VectorType.COL_TYPE:
            assert 0 <= idx < self.shape[1]
            newmat = []
            for _i in range(self.shape[0]):
                newmat.append([])
                for _j in range(self.shape[1]):
                    newmat[-1].append(self.data[_i][_j] if _j != idx else (self.data[_i][_j] * times))
            return Matrix(newmat)

    def std_plus(self, typ, frm, idx, times = 1):
        assert type(typ) == str and typ.lower() in Constants.VectorType.ALL_TYPE and times
        if typ.lower() in Constants.VectorType.ROW_TYPE:
            assert 0 <= frm < self.shape[0] and 0 <= idx < self.shape[0]
            newmat = []
            for _i in range(self.shape[0]):
                newmat.append([])
                for _j in range(self.shape[1]):
                    newmat[-1].append(self.data[_i][_j] + (0 if _i != idx else (self.data[frm][_j] * times)))
            return Matrix(newmat)
        elif typ.lower() in Constants.VectorType.COL_TYPE:
            assert 0 <= frm < self.shape[1] and 0 <= idx < self.shape[1]
            newmat = []
            for _i in range(self.shape[0]):
                newmat.append([])
                for _j in range(self.shape[1]):
                    newmat[-1].append(self.data[_i][_j] + (0 if _j != idx else (self.data[_i][frm] * times)))
            return Matrix(newmat)

    def gaussian(self, typ):
        assert type(typ) == str and typ.lower() in Constants.VectorType.ALL_TYPE
        newmat = self.copy
        if typ.lower() in Constants.VectorType.ROW_TYPE:
            for i in range(self.shape[0] - 1):
                for j in range(i + 1, self.shape[0]):
                    _data = newmat.data[j][i] * (-1)
                    newmat = newmat.std_mtpl("r", j, newmat.data[i][i])
                    newmat = newmat.std_plus("r", i, j, _data)
            return newmat
        elif typ.lower() in Constants.VectorType.COL_TYPE:
            for i in range(self.shape[1] - 1):
                for j in range(i + 1, self.shape[1]):
                    _data = newmat.data[i][j] * (-1)
                    newmat = newmat.std_mtpl("c", j, newmat.data[i][i])
                    newmat = newmat.std_plus("c", i, j, _data)
            return newmat

    @property
    def rank(self):
        assert self.issquare
        newmat = self.gaussian("r")
        rnk = 0
        for idx in range(self.shape[0]):
            rnk += 1 if newmat.data[idx][idx] else 0
        return rnk

    T = transposition
    det = determinant
    R = rank
    I = inverse

def zeros(shape):
    if type(shape) == int and shape > 0:
        return Matrix([ [ 0 for j in range(shape) ] for i in range(shape) ])
    elif type(shape) in Constants.ITER_TYPE and len(shape) == 2:
        return Matrix([ [ 0 for j in range(shape[1]) ] for i in range(shape[0]) ])
    else:
        raise AssertionError

def identity(shape):
    assert type(shape) == int and shape > 0
    return Matrix([ [ (1 if i == j else 0) for j in range(shape) ] for i in range(shape) ])

def ones(shape):
    if type(shape) == int and shape > 0:
        return Matrix([ [ 1 for j in range(shape) ] for i in range(shape) ])
    elif type(shape) in Constants.ITER_TYPE and len(shape) == 2:
        return Matrix([ [ 1 for j in range(shape[1]) ] for i in range(shape[0]) ])
    else:
        raise AssertionError

def hadamard(v, u):
    assert type(v) == type(u) == Matrix and v.shape == u.shape
    return Matrix([ [ (v.data[i][j] * u.data[i][j]) for j in range(v.shape[1]) ] for i in range(v.shape[0]) ])

class Examples(object):
    A = Matrix([ [ 1 , 2 , 3 ], [ 4 , 5 , 6 ], [ 7 , 8 , 0 ] ])
    B = Matrix([ [ 1 , 2 , 1 ], [ 1 , 1 , 2 ], [ 2 , 1 , 1 ] ])
    C = Matrix([ [ 5 , 2 , 4 ], [ 3 , 8 , 2 ], [ 6 , 0 , 4 ], [ 0 , 1 , 6 ] ])
    D = Matrix([ [ 2 , 4 ], [ 1 , 3 ], [ 3 , 2 ] ])
    E = Matrix([ [ 1 , 1 , (-1) , 2 ], [ (-1) , (-1) , (-4) , 1 ], [ 2 , 4 , (-6), 1 ], [ 1 , 2 , 2 , 2 ] ])
    F = Matrix([ [ 3 , 1 , 1 , 1 ], [ 1 , 3 , 1 , 1 ], [ 1 , 1 , 3 , 1 ], [ 1 , 1 , 1 , 3 ] ])
    G = Matrix([ [ 0 , 0 , 0 , 0 , 0 , 0 ], [ 1 , 0 , 0 , 0 , 0 , 0 ], [ 0 , 1 , 0 , 0 , 0 , 0 ], [ 0 , 0 , 1 , 0 , 0 , 0 ], [ 0 , 0 , 0 , 1 , 0 , 0 ], [ 0 , 0 , 0 , 0 , 1 , 0 ] ])
    H = Matrix([
        [ 1 , 2 , 3 , 0 , 0 , 0 , 0 , 0 ],
        [ 4 , 5 , 6 , 0 , 0 , 0 , 0 , 0 ],
        [ 7 , 8 , 9 , 0 , 10, 20, 30, 40],
        [ 0 , 0 , 0 , 1 , 2 , 0 , 0 , 0 ],
        [ 0 , 0 , 0 , 3 , 4 , 0 , 0 , 0 ],
        [ 0 , 60, 0 , 0 , 0 , 4 , 5 , 6 ],
        [ 0 , 0 , 0 , 0 , 0 , 7 , 8 , 9 ],
        [ 0 , 0 , 0 , 0 , 0 , 10, 11, 12]
    ])

if __name__ == "__main__":
    print(Examples.H.det)
