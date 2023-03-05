r"""
Tests for the Sage <-> PARI interface

    >>> pari.polchebyshev(10)
    512*x^10 - 1280*x^8 + 1120*x^6 - 400*x^4 + 50*x^2 - 1
    >>> pari("x^3 + 1").polsturm(-1, 1) == 1
    True
    >>> pari.prime(10)
    29
    >>> pari.primes(10)
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    >>> pari.primes(end=20)
    [2, 3, 5, 7, 11, 13, 17, 19]
    >>> pari.polcyclo(8, 2)
    17
    >>> pari('x^-2').Strtex()
    "\\frac{1}{x^2}"
    >>> pari(10).eulerphi()
    4
    >>> pari("x^3 + 5*x").polrecip()
    5*x^2 + 1
    >>> nf = pari("x^2 + 1").nfinit()
    >>> id = nf.idealhnf(2)
    >>> nf.idealintersect(id, id)
    [2, 0; 0, 2]
    >>> e = pari([1,0,1,-19,26]).ellinit()
    >>> e.elltors()
    [12, [6, 2], [[1, 2], [3, -2]]]
    >>> pari("Mod(2,5)").znorder()
    4

A long list of doctests which used to be part of manually written code
which is now automatically generated:

Reading a gp file::

    >>> import tempfile, os
    >>> handle, gpfilename = tempfile.mkstemp(text=True)
    >>> with open(gpfilename, 'wb+') as gpfile:
    ...   n = gpfile.write(bytes("mysquare(n) = {\n n^2;\n}\npolcyclo(5)\n".encode('ascii')))
    ...   gpfile.flush()
    ...
    >>> pari.read(gpfilename)
    x^4 + x^3 + x^2 + x + 1
    >>> pari('mysquare(12)')
    144
    >>> os.close(handle)
    >>> os.unlink(gpfilename)

Constants::

    >>> pari.euler()
    0.577215664901533
    >>> pari.pi()
    3.14159265358979
    >>> old_precision = pari.set_real_precision(100)
    >>> pari.euler(precision=100)
    0.577215664901532860606512090082...
    >>> pari.pi(precision=100)
    3.141592653589793238462643383279...
    >>> pari.set_real_precision(old_precision)
    100

Polynomial functions::

    >>> pari('2*x^2 + 2').content()
    2
    >>> pari("4*x^3 - 2*x/3 + 2/5").content()
    2/15

    >>> x = pari('y^8+6*y^6-27*y^5+1/9*y^2-y+1')
    >>> x.newtonpoly(3)
    [1, 1, -1/3, -1/3, -1/3, -1/3, -1/3, -1/3]

    >>> f = pari("x^2 + y^3 + x*y")
    >>> f
    x^2 + y*x + y^3
    >>> f.polcoeff(1)
    y
    >>> f.polcoeff(3)
    0
    >>> f.polcoeff(3, "y")
    1
    >>> f.polcoeff(1, "y")
    x

    >>> pari("x^2 + 1").poldisc()
    -4

    >>> pari.pollegendre(7)
    429/16*x^7 - 693/16*x^5 + 315/16*x^3 - 35/16*x
    >>> pari.pollegendre(7, 'z')
    429/16*z^7 - 693/16*z^5 + 315/16*z^3 - 35/16*z
    >>> pari.pollegendre(0)
    1

    >>> pari.polcyclo(8)
    x^4 + 1
    >>> pari.polcyclo(7, 'z')
    z^6 + z^5 + z^4 + z^3 + z^2 + z + 1
    >>> pari.polcyclo(1)
    x - 1

Power series::

    >>> f = pari('x+x^2+x^3+O(x^4)'); f
    x + x^2 + x^3 + O(x^4)
    >>> g = f.serreverse(); g
    x - x^2 + x^3 + O(x^4)
    >>> f.subst('x',g)
    x + O(x^4)
    >>> g.subst('x',f)
    x + O(x^4)

Random seed::

    >>> a = pari.getrand()
    >>> a.type()
    't_INT'

Constructors::

    >>> v = pari([1,2,3])
    >>> v
    [1, 2, 3]
    >>> v.type()
    't_VEC'
    >>> w = v.List()
    >>> w
    List([1, 2, 3])
    >>> w.type()
    't_LIST'

    >>> x = pari(5)
    >>> x.type()
    't_INT'
    >>> y = x.Mat()
    >>> y
    Mat(5)
    >>> y.type()
    't_MAT'
    >>> x = pari('[1,2;3,4]')
    >>> x.type()
    't_MAT'
    >>> x = pari('[1,2,3,4]')
    >>> x.type()
    't_VEC'
    >>> y = x.Mat()
    >>> y
    Mat([1, 2, 3, 4])
    >>> y.type()
    't_MAT'

    >>> v = pari('[1,2;3,4]').Vec(); v
    [[1, 3]~, [2, 4]~]
    >>> v.Mat()
    [1, 2; 3, 4]
    >>> v = pari('[1,2;3,4]').Col(); v
    [[1, 2], [3, 4]]~
    >>> v.Mat()
    [1, 2; 3, 4]

    >>> z = pari(3)
    >>> x = z.Mod(pari(7))
    >>> x
    Mod(3, 7)
    >>> x**2
    Mod(2, 7)
    >>> x**100
    Mod(4, 7)
    >>> x.type()
    't_INTMOD'
    >>> f = pari('x^2 + x + 1')
    >>> g = pari('x')
    >>> a = g.Mod(f)
    >>> a
    Mod(x, x^2 + x + 1)
    >>> a*a
    Mod(-x - 1, x^2 + x + 1)
    >>> a.type()
    't_POLMOD'

    >>> v = pari('[1,2,3,4]')
    >>> f = v.Pol()
    >>> f
    x^3 + 2*x^2 + 3*x + 4
    >>> f*f
    x^6 + 4*x^5 + 10*x^4 + 20*x^3 + 25*x^2 + 24*x + 16

    >>> v = pari('[1,2;3,4]')
    >>> v.Pol()
    [1, 3]~*x + [2, 4]~

    >>> v = pari('[1,2,3,4]')
    >>> f = v.Polrev()
    >>> f
    4*x^3 + 3*x^2 + 2*x + 1
    >>> v.Pol()
    x^3 + 2*x^2 + 3*x + 4
    >>> v.Polrev('y')
    4*y^3 + 3*y^2 + 2*y + 1

    >>> f
    4*x^3 + 3*x^2 + 2*x + 1
    >>> f.Polrev()
    4*x^3 + 3*x^2 + 2*x + 1
    >>> v = pari('[1,2;3,4]')
    >>> v.Polrev()
    [2, 4]~*x + [1, 3]~

    >>> pari(3).Qfb(7, 1)
    Qfb(3, 7, 1)
    >>> pari(3).Qfb(7, 2)
    Traceback (most recent call last):
    ...
    cypari_pari.PariError: domain error in Qfb: issquare(disc) = 1

    >>> pari([1,5,2]).Set()
    [1, 2, 5]
    >>> pari([]).Set()
    []
    >>> pari([1,1,-1,-1,3,3]).Set()
    [-1, 1, 3]
    >>> pari(1).Set()
    [1]
    >>> pari('1/(x*y)').Set()
    [1/(y*x)]
    >>> pari('["bc","ab","bc"]').Set()
    ["ab", "bc"]

    >>> pari([65,66,123]).Strchr()
    "AB{"
    >>> pari('"Sage"').Vecsmall()
    Vecsmall([83, 97, 103, 101])
    >>> _.Strchr()
    "Sage"
    >>> pari([83, 97, 103, 101]).Strchr()
    "Sage"

Basic functions::

     >>> pari(0).binary()
     []
     >>> pari(-5).binary()
     [1, 0, 1]
     >>> pari(5).binary()
     [1, 0, 1]
     >>> pari(2005).binary()
     [1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1]
     >>> pari('"2"').binary()
     Traceback (most recent call last):
     ...
     PariError: incorrect type in binary (t_STR)

    >>> pari(1.4).ceil()
    2
    >>> pari(-1.4).ceil()
    -1
    >>> pari('3/4').ceil()
    1
    >>> pari('x').ceil()
    x
    >>> pari('(x^2+x+1)/x').ceil()
    x + 1
    >>> pari('x^2+5*x+2.5').ceil()
    x^2 + 5*x + 2.50000000000000

    >>> x = pari(-2).Mod(5)
    >>> x.centerlift()
    -2
    >>> x.lift()
    3
    >>> f = pari('x-1').Mod('x^2 + 1')
    >>> f.centerlift()
    x - 1
    >>> f.lift()
    x - 1
    >>> f = pari('x-y').Mod('x^2+1')
    >>> f
    Mod(x - y, x^2 + 1)
    >>> f.centerlift('x')
    x - y
    >>> f.centerlift('y')
    Mod(x - y, x^2 + 1)
    >>> pari("Mod(3,5)").lift_centered()
    -2

    >>> pari([0,1,2,3,4]).component(1)
    0
    >>> pari([0,1,2,3,4]).component(2)
    1
    >>> pari([0,1,2,3,4]).component(4)
    3
    >>> pari('x^3 + 2').component(1)
    2
    >>> pari('x^3 + 2').component(2)
    0
    >>> pari('x^3 + 2').component(4)
    1
    >>> pari('x').component(0)
    Traceback (most recent call last):
    ...
    PariError: non-existent component: index < 1

    >>> pari('x+1').conj()
    x + 1
    >>> pari('x+I').conj()
    x - I
    >>> pari('1/(2*x+3*I)').conj()
    1/(2*x - 3*I)
    >>> pari([1,2,'2-I','Mod(x,x^2+1)', 'Mod(x,x^2-2)']).conj()
    [1, 2, 2 + I, Mod(-x, x^2 + 1), Mod(-x, x^2 - 2)]
    >>> pari('Mod(x,x^2-2)').conj()
    Mod(-x, x^2 - 2)
    >>> pari('Mod(x,x^3-3)').conj()
    Traceback (most recent call last):
    ...
    PariError: incorrect type in gconj (t_POLMOD)

    >>> pari('Mod(1+x,x^2-2)').conjvec()
    [-0.414213562373095, 2.41421356237310]~
    >>> pari('Mod(x,x^3-3)').conjvec()
    [1.44224957030741, -0.721124785153704 - 1.24902476648341*I, -0.721124785153704 + 1.24902476648341*I]~
    >>> save = pari.set_real_precision(57)
    >>> pari('Mod(1+x,x^2-2)').conjvec(precision=192)[0]
    -0.414213562373095048801688724209698078569671875376948073177
    >>> restore = pari.set_real_precision(save)
    >>> pari('5/9').denominator()
    9
    >>> pari('(x+1)/(x-2)').denominator()
    x - 2
    >>> pari('2/3 + 5/8*x + 7/3*x^2 + 1/5*y').denominator()
    1
    >>> pari('2/3*x').denominator()
    1
    >>> pari('[2/3, 5/8, 7/3, 1/5]').denominator()
    120

    >>> pari(5/9).floor()
    0
    >>> pari(11/9).floor()
    1
    >>> pari(1.17).floor()
    1
    >>> pari([1.5,2.3,4.99]).floor()
    [1, 2, 4]
    >>> pari([[1.1,2.2],[3.3,4.4]]).floor()
    [[1, 2], [3, 4]]
    >>> pari('x').floor()
    x
    >>> pari('(x^2+x+1)/x').floor()
    x + 1
    >>> pari('x^2+5*x+2.5').floor()
    x^2 + 5*x + 2.50000000000000
    >>> pari('"hello world"').floor()
    Traceback (most recent call last):
    ...
    PariError: incorrect type in gfloor (t_STR)

    >>> pari(1.75).frac()
    0.750000000000000
    >>> pari('sqrt(2)').frac()
    0.414213562373095
    >>> pari('sqrt(-2)').frac()
    Traceback (most recent call last):
    ...
    PariError: incorrect type in gfloor (t_COMPLEX)

    >>> pari('1+2*I').imag()
    2
    >>> pari('sqrt(-2)').imag()
    1.41421356237310
    >>> pari('x+I').imag()
    1
    >>> pari('x+2*I').imag()
    2
    >>> pari('(1+I)*x^2+2*I').imag()
    x^2 + 2
    >>> pari('[1,2,3] + [4*I,5,6]').imag()
    [4, 0, 0]

    >>> x = pari('x')
    >>> a = x.Mod('x^3 + 17*x + 3')
    >>> a
    Mod(x, x^3 + 17*x + 3)
    >>> b = a**4; b
    Mod(-17*x^2 - 3*x, x^3 + 17*x + 3)
    >>> b.lift()
    -17*x^2 - 3*x

    >>> pari.pi().sign()
    1
    >>> pari(0).sign()
    0
    >>> pari(-1/2).sign()
    -1
    >>> pari('I').sign()
    Traceback (most recent call last):
    ...
    PariError: incorrect type in gsigne (t_COMPLEX)

    >>> y = pari('y')
    >>> x = pari('9') + y - y
    >>> x
    9
    >>> x.type()
    't_POL'
    >>> x.factor()
    matrix(0,2)
    >>> pari('9').factor()
    Mat([3, 2])
    >>> x.simplify()
    9
    >>> x.simplify().factor()
    Mat([3, 2])
    >>> x = pari('1.5 + 0*I')
    >>> x.type()
    't_REAL'
    >>> x.simplify()
    1.50000000000000
    >>> y = x.simplify()
    >>> y.type()
    't_REAL'

    >>> pari(2).sqr()
    4
    >>> pari("1+O(2^5)").sqr()
    1 + O(2^6)
    >>> pari("1+O(2^5)")*pari("1+O(2^5)")
    1 + O(2^5)
    >>> x = pari("1+O(2^5)"); x*x
    1 + O(2^6)

    >>> x = pari("x"); y = pari("y")
    >>> f = pari('x^3 + 17*x + 3')
    >>> f.subst(x, y)
    y^3 + 17*y + 3
    >>> f.subst(x, "z")
    z^3 + 17*z + 3
    >>> f.subst(x, "z")**2
    z^6 + 34*z^4 + 6*z^3 + 289*z^2 + 102*z + 9
    >>> f.subst(x, "x+1")
    x^3 + 3*x^2 + 20*x + 21
    >>> f.subst(x, "xyz")
    xyz^3 + 17*xyz + 3
    >>> f.subst(x, "xyz")**2
    xyz^6 + 34*xyz^4 + 6*xyz^3 + 289*xyz^2 + 102*xyz + 9

    >>> pari(9).valuation(3)
    2
    >>> pari(9).valuation(9)
    1
    >>> x = pari(9).Mod(27); x.valuation(3)
    2
    >>> pari('5/3').valuation(3)
    -1
    >>> pari('9 + 3*x + 15*x^2').valuation(3)
    1
    >>> pari([9,3,15]).valuation(3)
    1
    >>> pari('9 + 3*x + 15*x^2 + O(x^5)').valuation(3)
    1
    >>> pari('x^2*(x+1)^3').valuation(pari('x+1'))
    3
    >>> pari('x + O(x^5)').valuation('x')
    1
    >>> pari('2*x^2 + O(x^5)').valuation('x')
    2
    >>> pari(0).valuation(3)
    +oo

    >>> pari('x^2 + x -2').variable()
    x
    >>> pari('1+2^3 + O(2^5)').variable()
    2
    >>> pari('x+y0').variable()
    x
    >>> pari('y0+z0').variable()
    y0

Bitwise functions::

    >>> pari(8).bitand(4)
    0
    >>> pari(8).bitand(8)
    8
    >>> pari(6).binary()
    [1, 1, 0]
    >>> pari(7).binary()
    [1, 1, 1]
    >>> pari(6).bitand(7)
    6
    >>> pari(19).bitand(-1)
    19
    >>> pari(-1).bitand(-1)
    -1

    >>> pari(10).bitneg()
    -11
    >>> pari(1).bitneg()
    -2
    >>> pari(-2).bitneg()
    1
    >>> pari(-1).bitneg()
    0
    >>> pari(569).bitneg()
    -570
    >>> pari(569).bitneg(10)
    454
    >>> 454 % 2**10
    454
    >>> -570 % 2**10
    454

    >>> pari(14).bitnegimply(0)
    14
    >>> pari(8).bitnegimply(8)
    0
    >>> pari(8+4).bitnegimply(8)
    4

    >>> pari(14).bitor(0)
    14
    >>> pari(8).bitor(4)
    12
    >>> pari(12).bitor(1)
    13
    >>> pari(13).bitor(1)
    13

    >>> pari(6).bitxor(4)
    2
    >>> pari(0).bitxor(4)
    4
    >>> pari(6).bitxor(0)
    6

Transcendental functions::

    >>> x = pari("-27.1")
    >>> x.abs()
    27.1000000000000
    >>> save = pari.set_real_precision(38)
    >>> pari('1+I').abs(precision=128)
    1.4142135623730950488016887242096980786
    >>> restore = pari.set_real_precision(save)
    >>> pari('x-1.2*x^2').abs()
    1.20000000000000*x^2 - x
    >>> pari('-2 + t + O(t^2)').abs()
    2 - t + O(t^2)

    >>> pari(0.5).acos()
    1.04719755119660
    >>> pari('1/2').acos()
    1.04719755119660
    >>> pari(1.1).acos()
    0.443568254385115*I
    >>> pari('1.1+I').acos()
    0.849343054245252 - 1.09770986682533*I

    >>> pari(2).acosh()
    1.31695789692482
    >>> pari(0).acosh()
    1.57079632679490*I
    >>> pari('I').acosh()
    0.881373587019543 + 1.57079632679490*I

    >>> pari(2).agm(2)
    2.00000000000000
    >>> pari(0).agm(1)
    0
    >>> pari(1).agm(2)
    1.45679103104691
    >>> pari('1+I').agm(-3)
    -0.964731722290876 + 1.15700282952632*I

    >>> pari('2+I').arg()
    0.463647609000806

    >>> pari(pari(0.5).sin()).asin()
    0.500000000000000
    >>> pari(2).asin()
    1.57079632679490 - 1.31695789692482*I

    >>> pari(2).asinh()
    1.44363547517881
    >>> pari('2+I').asinh()
    1.52857091948100 + 0.427078586392476*I

    >>> pari(1).atan()
    0.785398163397448
    >>> pari('1.5+I').atan()
    1.10714871779409 + 0.255412811882995*I

    >>> pari(0).atanh()
    0.E-19
    >>> pari(2).atanh()
    0.549306144334055 - 1.57079632679490*I

    >>> pari(2).besselh1(3)
    0.486091260585891 - 0.160400393484924*I
    >>> pari(2).besselh2(3)
    0.486091260585891 + 0.160400393484924*I
    >>> pari(2).besselj(3)
    0.486091260585891
    >>> pari(2).besseljh(3)
    0.412710032209716
    >>> pari(2).besseli(3)
    2.24521244092995
    >>> pari(2).besseli(3+1j)
    1.12539407613913 + 2.08313822670661*I
    >>> pari('2+I').besseln(3)
    -0.280775566958244 - 0.486708533223726*I

    >>> pari(1.5).cos()
    0.0707372016677029
    >>> pari('1+I').cos()
    0.833730025131149 - 0.988897705762865*I
    >>> pari('x+O(x^8)').cos()
    1 - 1/2*x^2 + 1/24*x^4 - 1/720*x^6 + 1/40320*x^8 + O(x^9)

    >>> pari(1.5).cosh()
    2.35240961524325
    >>> pari('1+I').cosh()
    0.833730025131149 + 0.988897705762865*I
    >>> pari('x+O(x^8)').cosh()
    1 + 1/2*x^2 + 1/24*x^4 + 1/720*x^6 + 1/40320*x^8 + O(x^9)
    >>> pari(5).cotan()
    -0.295812915532746
    >>> x = pari.pi()
    >>> pari(x).cotan()
    1.99339881490586 E19
    >>> pari(1).dilog()
    1.64493406684823
    >>> pari('1+I').dilog()
    0.616850275068085 + 1.46036211675312*I

    >>> pari(1).erfc()
    0.157299207050285

    >>> pari('I').eta()
    0.998129069925959

    >>> pari(0).exp()
    1.00000000000000
    >>> pari(1).exp()
    2.71828182845905
    >>> pari('x+O(x^8)').exp()
    1 + x + 1/2*x^2 + 1/6*x^3 + 1/24*x^4 + 1/120*x^5 + 1/720*x^6 + 1/5040*x^7 + O(x^8)

    >>> pari(2).gamma()
    1.00000000000000
    >>> pari(5).gamma()
    24.0000000000000
    >>> pari('1+I').gamma()
    0.498015668118356 - 0.154949828301811*I
    >>> pari(-1).gamma()
    Traceback (most recent call last):
    ...
    PariError: domain error in gamma: argument = non-positive integer
    >>> pari(2).gammah()
    1.32934038817914
    >>> pari(5).gammah()
    52.3427777845535
    >>> pari('1+I').gammah()
    0.575315188063452 + 0.0882106775440939*I

    >>> pari(1).hyperu(2,3)
    0.333333333333333

    >>> pari('1+I').incgam(3-1j)
    -0.0458297859919946 + 0.0433696818726677*I
    >>> pari(1).incgamc(2)
    0.864664716763387

    >>> pari(5).log()
    1.60943791243410
    >>> pari('I').log()
    1.57079632679490*I

    >>> pari(100).lngamma()
    359.134205369575
    >>> pari(100).log_gamma()
    359.134205369575

    >>> pari(1).psi()
    -0.577215664901533

    >>> pari(1).sin()
    0.841470984807897
    >>> pari('1+I').sin()
    1.29845758141598 + 0.634963914784736*I

    >>> pari(0).sinh()
    0.E-19
    >>> pari('1+I').sinh()
    0.634963914784736 + 1.29845758141598*I

    >>> pari(2).sqrt()
    1.41421356237310

    >>> pari(8).sqrtint()
    2
    >>> pari(10**100).sqrtint()
    100000000000000000000000000000000000000000000000000

    >>> pari(2).tan()
    -2.18503986326152
    >>> pari('I').tan()
    0.761594155955765*I

    >>> pari(1).tanh()
    0.761594155955765
    >>> z = pari(1j); z
    1.00000000000000*I
    >>> result = z.tanh()
    >>> result.real() <= 1e-18
    True
    >>> result.imag()
    1.55740772465490

    >>> pari('2+O(7^5)').teichmuller()
    2 + 4*7 + 6*7^2 + 3*7^3 + O(7^5)

    >>> pari(0.5).theta(2)
    1.63202590295260

    >>> pari(0.5).thetanullk(1)
    0.548978532560341

    >>> pari('I').weber()
    1.18920711500272
    >>> pari('I').weber(1)
    1.09050773266526
    >>> pari('I').weber(2)
    1.09050773266526

    >>> pari(2).zeta()
    1.64493406684823
    >>> x = pari.pi()**2/6
    >>> pari(x)
    1.64493406684823
    >>> pari(3).zeta()
    1.20205690315959
    >>> pari('1+5*7+2*7^2+O(7^3)').zeta()
    4*7^-2 + 5*7^-1 + O(7^0)

Linear algebra::

    >>> pari('[1,2,3; 4,5,6; 7,8,9]').matadjoint()
    [-3, 6, -3; 6, -12, 6; -3, 6, -3]
    >>> pari('[A,B,C; D,E,F; G,H,I]').matadjoint()
    [(I*E - H*F), (-I*B + H*C), (F*B - E*C); (-I*D + G*F), I*A - G*C, -F*A + D*C; (H*D - G*E), -H*A + G*B, E*A - D*B]
    >>> pari('[1,1;1,-1]').matsolve(pari('[1;0]'))
    [1/2; 1/2]

    >>> D = pari('[3,4]~')
    >>> B = pari('[1,2]~')
    >>> M = pari('[1,2;3,4]')
    >>> M.matsolvemod(D, B)
    [10, 0]~
    >>> M.matsolvemod(3, 1)
    [2, 1]~
    >>> M.matsolvemod(pari('[3,0]~'), pari('[1,2]~'))
    [6, -4]~
    >>> M2 = pari('[1,10;9,18]')
    >>> M2.matsolvemod(3, pari('[2,3]~'), 1)
    [[2, 0]~, [3, 2; 0, 1]]
    >>> M2.matsolvemod(9, pari('[2,3]~'))
    0
    >>> M2.matsolvemod(9, pari('[2,45]~'), 1)
    [[2, 0]~, [9, 8; 0, 1]]

    >>> pari('[1,2,3;4,5,6;7,8,9]').matker()
    [1; -2; 1]
    >>> pari('[1,2,3;4,5,6;7,8,9]').matker(1)
    [1; -2; 1]
    >>> pari('matrix(3,3,i,j,i)').matker()
    [-1, -1; 1, 0; 0, 1]
    >>> pari('[1,2,3;4,5,6;7,8,9]*Mod(1,2)').matker()
    [Mod(1, 2); Mod(0, 2); Mod(1, 2)]

    >>> pari('[1,2; 3,4]').matdet(0)
    -2
    >>> pari('[1,2; 3,4]').matdet(1)
    -2

    >>> pari('[1,2; 3,4]').trace()
    5

    >>> pari('[1,2,3; 4,5,6;  7,8,9]').mathnf()
    [6, 1; 3, 1; 0, 1]

    >>> M = pari('[1,2,3; 4,5,6; 7,8,11]')
    >>> d = M.matdet()
    >>> M.mathnfmod(d)
    [6, 4, 3; 0, 1, 0; 0, 0, 1]
    >>> M = pari('[1,0,0; 0,2,0; 0,0,6]')
    >>> M.mathnfmod(6)
    [1, 0, 0; 0, 1, 0; 0, 0, 6]
    >>> M.mathnfmod(12)
    [1, 0, 0; 0, 2, 0; 0, 0, 6]

    >>> M = pari('[1,0,0; 0,2,0; 0,0,6]')
    >>> M.mathnfmodid(6)
    [1, 0, 0; 0, 2, 0; 0, 0, 6]
    >>> M.mathnfmod(6)
    [1, 0, 0; 0, 1, 0; 0, 0, 6]

    >>> pari('[1,2,3; 4,5,6; 7,8,9]').matsnf()
    [0, 3, 1]

    >>> a = pari('[1,2; 3,4]')
    >>> a.matfrobenius()
    [0, 2; 1, 5]
    >>> a.matfrobenius(flag=1)
    [x^2 - 5*x - 2]
    >>> a.matfrobenius(2)
    [[0, 2; 1, 5], [1, -1/3; 0, 1/3]]
    >>> v = a.matfrobenius(2)
    >>> v[0]
    [0, 2; 1, 5]
    >>> v[1]**(-1)*v[0]*v[1]
    [1, 2; 3, 4]
    >>> t = pari('[3, -2, 0, 0; 0, -2, 0, 1; 0, -1, -2, 2; 0, -2, 0, 2]')
    >>> t.matfrobenius()
    [0, 0, 0, -12; 1, 0, 0, -2; 0, 1, 0, 8; 0, 0, 1, 1]
    >>> t.charpoly('x')
    x^4 - x^3 - 8*x^2 + 2*x + 12
    >>> t.matfrobenius(1)
    [x^4 - x^3 - 8*x^2 + 2*x + 12]

Quadratic forms::

    >>> A = pari('[1,2,3; 2,5,5; 3,5,11]')
    >>> A.qfminim(10, 5)
    [146, 10, [17, 14, 15, 16, 13; -4, -3, -3, -3, -2; -3, -3, -3, -3, -3]]
    >>> A.qfminim()
    [6, 1, [5, 2, 1; -1, -1, 0; -1, 0, 0]]
    >>> A = pari('[1.0,2,3; 2,5,5; 3,5,11]')
    >>> A.qfminim(5, m=5, flag=2)
    [10, 5.00000000000000, [-5, -10, -2, -7, 3; 1, 2, 1, 2, 0; 1, 2, 0, 1, -1]]
    >>> M = pari('matdiagonal([1,1,-1])')
    >>> P = M.qfparam([0,1,-1]); P
    [0, -2, 0; 1, 0, -1; -1, 0, -1]
    >>> v = P * pari('[x^2, x*y, y^2]~'); v
    [-2*y*x, x^2 - y^2, -x^2 - y^2]~
    >>> v(x=2, y=1)
    [-4, 3, -5]~
    >>> v(x=3,y=8)
    [-48, -55, -73]~
    >>> 48**2 + 55**2 == 73**2
    True

    >>> M = pari('matdiagonal([1,2,3,4,-5])')
    >>> M.qfsolve()
    [0, 1, -1, 0, -1]~
    >>> M = pari('matdiagonal([4,-9])')
    >>> M.qfsolve()
    [6, 4]~
    >>> M = pari('matdiagonal([1,1,1,1,1])')
    >>> M.qfsolve()
    -1
    >>> M = pari('matdiagonal([1,1,-3])')
    >>> M.qfsolve()
    3
    >>> M = pari('matdiagonal([1,-42])')
    >>> M.qfsolve()
    -2
    >>> M = pari('matdiagonal([1,-1,0,0])')
    >>> M.qfsolve()
    [0, 0; 0, 0; 1, 0; 0, 1]

Number-theoretical functions::

    >>> n = pari.set_real_precision(210)
    >>> w1 = pari('z1=2-sqrt(26); (z1+I)/(z1-I)')
    >>> f = w1.algdep(12); f
    545*x^11 - 297*x^10 - 281*x^9 + 48*x^8 - 168*x^7 + 690*x^6 - 168*x^5 + 48*x^4 - 281*x^3 - 297*x^2 + 545*x
    >>> f(w1).abs() < 1.0e-200
    True
    >>> f.factor()
    [x, 1; x + 1, 2; x^2 + 1, 1; x^2 + x + 1, 1; 545*x^4 - 1932*x^3 + 2790*x^2 - 1932*x + 545, 1]
    >>> pari.set_real_precision(n)
    210

    >>> pari(6).binomial(2)
    15
    >>> pari('x+1').binomial(3)
    1/6*x^3 - 1/6*x
    >>> pari('2+x+O(x^2)').binomial(3)
    1/3*x + O(x^2)

    >>> pari(10).eulerphi()
    4

    >>> x = pari('x')
    >>> pari(10).gcd(15)
    5
    >>> pari([5, 'y']).gcd()
    1
    >>> pari([x, x**2]).gcd()
    x
    >>> pari(10).lcm(15)
    30
    >>> pari([5, 'y']).lcm()
    5*y
    >>> pari([10, x, x**2]).lcm()
    10*x^2

    >>> pari(20).numbpart()
    627
    >>> pari(100).numbpart()
    190569292

    >>> pari(10).numdiv()
    4

    >>> pari(7).primepi()
    4
    >>> pari(100).primepi()
    25
    >>> pari(1000).primepi()
    168
    >>> pari(100000).primepi()
    9592
    >>> pari(0).primepi()
    0
    >>> pari(-15).primepi()
    0
    >>> pari(500509).primepi()
    41581
    >>> pari(10**7).primepi()
    664579

    >>> pari(4).znprimroot()
    Mod(3, 4)
    >>> pari(10007**3).znprimroot()
    Mod(5, 1002101470343)
    >>> pari(2*109**10).znprimroot()
    Mod(236736367459211723407, 473472734918423446802)

    >>> pari(0).znstar()
    [2, [2], [-1]]
    >>> pari(96).znstar()
    [32, [8, 2, 2], [Mod(37, 96), Mod(31, 96), Mod(65, 96)]]
    >>> pari(-5).znstar()
    [4, [4], [Mod(2, 5)]]

    >>> g = pari(101).znprimroot(); g
    Mod(2, 101)
    >>> pari(5).znlog(g)
    24
    >>> g**24
    Mod(5, 101)
    >>> G = pari('2*101^10').znprimroot(); G
    Mod(110462212541120451003, 220924425082240902002)
    >>> pari(5).znlog(G)
    76210072736547066624
    >>> G**_ == 5
    True
    >>> N = pari('2^4*3^2*5^3*7^4*11')
    >>> g = pari(13).Mod(N)
    >>> (g**110).znlog(g)
    110
    >>> pari(6).znlog(pari(2).Mod(3))
    []

Finite fields::

    >>> x = pari('x')
    >>> (x**2+x+2).Mod(2).ffgen()
    x
    >>> (x**2+x+1).Mod(2).ffgen('a')
    a

    >>> pari(7).ffinit(11)
    Mod(1, 7)*x^11 + Mod(1, 7)*x^10 + Mod(4, 7)*x^9 + Mod(5, 7)*x^8 + Mod(1, 7)*x^7 + Mod(1, 7)*x^2 + Mod(1, 7)*x + Mod(6, 7)
    >>> pari(2003).ffinit(3)
    Mod(1, 2003)*x^3 + Mod(1, 2003)*x^2 + Mod(1993, 2003)*x + Mod(1995, 2003)
    >>> a = pari('ffinit(2,12)').ffgen()
    >>> g = a.ffprimroot()
    >>> (g**1234).fflog(g)
    1234
    >>> (a/a).fflog(g)
    0
    >>> b = g**5
    >>> ord = b.fforder(); ord
    819
    >>> (b**555).fflog(b, ord)
    555
    >>> (b**555).fflog(b, (ord, ord.factor()) )
    555

    >>> a = pari('ffinit(5, 80)').ffgen()
    >>> g = a.ffprimroot()
    >>> g.fforder()
    82718061255302767487140869206996285356581211090087890624
    >>> g.fforder((5**80-1, pari(5**80-1).factor()))
    82718061255302767487140869206996285356581211090087890624
    >>> (2*(a/a)).fforder(o=4)
    4

p-adic functions::

    >>> y = pari('11^-10 + 5*11^-7 + 11^-6 + O(11^-5)')
    >>> y.padicprec(11)
    -5
    >>> y.padicprec(17)
    Traceback (most recent call last):
    ...
    PariError: inconsistent moduli in padicprec: 11 != 17
    >>> pol = pari('O(3^5)*t^2 + O(3^6)*t + O(3^4)')
    >>> pol.padicprec(3)
    4

Elliptic curves::

    >>> e = pari([0,1,1,-2,0]).ellinit()
    >>> x = pari([1,0])
    >>> e.ellisoncurve([1,4])
    False
    >>> e.ellisoncurve(x)
    True
    >>> f = e.ellchangecurve([1,2,3,-1])

    >>> f[:5]
    [6, -2, -1, 17, 8]
    >>> x.ellchangepoint([1,2,3,-1])
    [-1, 4]
    >>> f.ellisoncurve([-1,4])
    True

    >>> e = pari([0, 5, 2, -1, 1]).ellinit()
    >>> e.ellglobalred()
    [20144, [1, -2, 0, -1], 1, [2, 4; 1259, 1], [[4, 2, 0, 1], [1, 5, 0, 1]]]
    >>> e = pari((1, -1, 1, -1, -14)).ellinit()
    >>> e.ellglobalred()
    [17, [1, 0, 0, 0], 4, Mat([17, 1]), [[1, 8, 0, 4]]]

    >>> e = pari([0, 1, 1, -2, 0]).ellinit()
    >>> e.elladd([1,0], [-1,1])
    [-3/4, -15/8]

    >>> e = pari([0, -1, 1, -10, -20]).ellinit()
    >>> e.ellak(6)
    2
    >>> e.ellak(2005)
    2
    >>> e.ellak(-1)
    0
    >>> e.ellak(0)
    0

    >>> E = pari((0,1,1,-2,0)).ellinit()
    >>> E.ellanalyticrank()
    [2, 1.51863300057685]
    >>> E.ellan(10)
    [1, -2, -2, 2, -3, 4, -5, 0, 1, 6]
    >>> e = pari([0, -1, 1, -10, -20]).ellinit()
    >>> e.ellap(2)
    -2
    >>> e.ellap(2003)
    4

    >>> e = pari([1,2,3,4,5]).ellinit()
    >>> e.ellglobalred()
    [10351, [1, -1, 0, -1], 1, [11, 1; 941, 1], [[1, 5, 0, 1], [1, 5, 0, 1]]]
    >>> f = e.ellchangecurve([1,-1,0,-1])
    >>> f[:5]
    [1, -1, 0, 4, 3]

    >>> e = pari([0,0,0,-82,0]).ellinit()
    >>> e.elleta()
    [3.60546360143265, 3.60546360143265*I]
    >>> w1, w2 = e.omega()
    >>> eta1, eta2 = e.elleta()
    >>> w1*eta2 - w2*eta1
    6.28318530717959*I

    >>> e = pari([0,1,1,-2,0]).ellinit().ellminimalmodel()[0]
    >>> e.ellheightmatrix([[1,0], [-1,1]])
    [0.476711659343740, 0.418188984498861; 0.418188984498861, 0.686667083305587]

    >>> e = pari([0,1,1,-2,0]).ellinit()
    >>> om = e.omega()
    >>> om
    [2.49021256085506, -1.97173770155165*I]
    >>> om.elleisnum(2)
    10.0672605281120
    >>> om.elleisnum(4)
    112.000000000000
    >>> om.elleisnum(100)
    2.15314248576078 E50

    >>> e = pari([0,0,0,0,1]).ellinit()
    >>> e.elllocalred(7)
    [0, 1, [1, 0, 0, 0], 1]
    >>> e = pari((0, 0, 1, 0, 0)).ellinit()
    >>> e.elllocalred(3)
    [3, 2, [1, 0, 0, 0], 1]
    >>> e = pari((0, -1, 0, 1, 0)).ellinit()
    >>> e.elllocalred(2)
    [3, 3, [1, 0, 0, 0], 2]
    >>> e = pari((0, 1, 0, -1, 0)).ellinit()
    >>> e.elllocalred(2)
    [2, 4, [1, 0, 0, 0], 3]
    >>> e = pari((0, -1, 1, -7820, -263580)).ellinit()
    >>> e.elllocalred(11)
    [1, 5, [1, 0, 0, 0], 1]
    >>> e = pari((1, 0, 1, -1, 0)).ellinit()
    >>> e.elllocalred(2)
    [1, 6, [1, 0, 0, 0], 2]
    >>> e = pari((1, 0, 1, 4, -6)).ellinit()
    >>> e.elllocalred(2)
    [1, 10, [1, 0, 0, 0], 2]
    >>> e = pari((0, 0, 0, -11, -14)).ellinit()
    >>> e.elllocalred(2)
    [5, -1, [1, 0, 0, 0], 1]
    >>> e = pari((0, -1, 0, -384, -2772)).ellinit()
    >>> e.elllocalred(2)
    [3, -2, [1, 0, 0, 0], 1]
    >>> e = pari((0, -1, 0, -24, -36)).ellinit()
    >>> e.elllocalred(2)
    [3, -3, [1, 0, 0, 0], 2]
    >>> e = pari((0, 1, 0, 4, 4)).ellinit()
    >>> e.elllocalred(2)
    [2, -4, [1, 0, 0, 0], 3]
    >>> e = pari((0, -1, 0, -4, 4)).ellinit()
    >>> e.elllocalred(2)
    [3, -5, [1, 0, 0, 0], 4]
    >>> e = pari((1, -1, 1, -167, -709)).ellinit()
    >>> e.elllocalred(3)
    [2, -10, [1, 0, 0, 0], 4]

    >>> e = pari([0,1,1,-2,0]).ellinit()
    >>> e.ellan(10)
    [1, -2, -2, 2, -3, 4, -5, 0, 1, 6]
    >>> e.elllseries(2.1)
    0.402838047956646
    >>> e.elllseries(1, precision=128).abs() < 2**-126
    True
    >>> e.elllseries(1, precision=256).abs() < 2**-254
    True
    >>> e.elllseries(-2)
    0
    >>> e.elllseries(2.1, A=1.1)
    0.402838047956646

    >>> e = pari((1, 0, 0, -1, 0)).ellinit()
    >>> e.ellorder([0,0])
    2
    >>> e.ellorder([1,0])
    0

    >>> e = pari([0,1,1,-2,0]).ellinit()
    >>> e.ellordinate(0)
    [0, -1]
    >>> e.ellordinate(pari('I'))
    [0.582203589721741 - 1.38606082464177*I, -1.58220358972174 + 1.38606082464177*I]
    >>> save=pari.set_real_precision(128)
    >>> e.ellordinate(pari('I'), precision=128)[0]
    0.58220358972174117723338947874993600727 - 1.38606082464176971853118342098336533447*I
    >>> restore = pari.set_real_precision(save)
    >>> e.ellordinate(pari('1+3*5^1+O(5^3)'))
    [4*5 + 5^2 + O(5^3), 4 + 3*5^2 + O(5^3)]
    >>> e.ellordinate('z+2*z^2+O(z^4)')
    [-2*z - 7*z^2 - 23*z^3 + O(z^4), -1 + 2*z + 7*z^2 + 23*z^3 + O(z^4)]
    >>> e.ellordinate(5)
    []
    >>> e.ellordinate(5.0)
    [11.3427192823270, -12.3427192823270]

    >>> e = pari([0,0,0,1,0]).ellinit()
    >>> e.ellpointtoz([0,0])
    1.85407467730137
    >>> e.ellpointtoz([0])
    0

    >>> e = pari([0,0,0,3,0]).ellinit()
    >>> p = [1,2]  # Point of infinite order
    >>> e.ellmul([0,0], 2)
    [0]
    >>> e.ellmul(p, 2)
    [1/4, -7/8]
    >>> q = e.ellmul(p, pari('1+I')); q
    [-2*I, 1 + I]
    >>> e.ellmul(q, pari('1-I'))
    [1/4, -7/8]

    # >>> for D in [-7, -8, -11, -12, -16, -19, -27, -28]:  # long time (1s)
    # ....:     hcpol = hilbert_class_polynomial(D)
    # ....:     j = hcpol.roots(multiplicities=False)[0]
    # ....:     t = (1728-j)/(27*j)
    # ....:     E = EllipticCurve([4*t,16*t^2])
    # ....:     P = E.point([0, 4*t])
    # ....:     assert(E.j_invariant() == j)
    # ....:     #
    # ....:     # Compute some CM number and its minimal polynomial
    # ....:     #
    # ....:     cm = pari('cm = (3*quadgen(%s)+2)'%D)
    # ....:     cm_minpoly = pari('minpoly(cm)')
    # ....:     #
    # ....:     # Evaluate cm_minpoly(cm)(P), which should be zero
    # ....:     #
    # ....:     e = pari(E)  # Convert E to PARI
    # ....:     P2 = e.ellmul(P, cm_minpoly[2]*cm + cm_minpoly[1])
    # ....:     P0 = e.elladd(e.ellmul(P, cm_minpoly[0]), e.ellmul(P2, cm))
    # ....:     assert(P0 == E(0))

    >>> e = pari([0,0,0,-82,0]).ellinit()
    >>> e.ellrootno() == -1
    True
    >>> e.ellrootno(2) == 1
    True
    >>> e.ellrootno(1009) == 1
    True

    >>> e = pari([0,0,0,1,0]).ellinit()
    >>> e.ellan(10)
    [1, 0, 0, 0, 2, 0, 0, 0, -3, 0]
    >>> e.ellsigma(pari('2+I'))
    1.43490215804166 + 1.80307856719256*I

    >>> e = pari([0, 1, 1, -2, 0]).ellinit()
    >>> e.ellsub([1,0], [-1,1])
    [0, 0]

    >>> e = pari([0,0,0,1,0]).ellinit()
    >>> e.ellzeta(1)
    1.06479841295883
    >>> e.ellzeta(pari('I-1'))
    -0.350122658523049 - 0.350122658523049*I

    >>> e = pari([0,0,0,1,0]).ellinit()
    >>> e.ellztopoint(pari('1+I')) # doctest: +ELLIPSIS
    [0.E-... - 1.02152286795670*I, -0.149072813701096 - 0.149072813701096*I]
    >>> e.ellztopoint(0)
    [0]

    >>> pari('I').ellj()
    1728.00000000000
    >>> pari('3*I').ellj()
    153553679.396729
    >>> pari('quadgen(-3)').ellj()
    0.E-54
    >>> save = pari.set_real_precision(76)
    >>> pari('quadgen(-7)').ellj(precision=256)
    -3375.000000000000000000000000000000000000000000000000000000000000000000000000
    >>> restore = pari.set_real_precision(save)
    >>> pari('-I').ellj()
    Traceback (most recent call last):
    ...
    PariError: domain error in modular function: Im(argument) <= 0

Quadratic class numbers::

    >>> pari(10009).qfbhclassno()
    0
    >>> pari(2).qfbhclassno()
    0
    >>> pari(0).qfbhclassno()
    -1/12
    >>> pari(4).qfbhclassno()
    1/2
    >>> pari(3).qfbhclassno()
    1/3
    >>> pari(23).qfbhclassno()
    3

    >>> pari(-4).qfbclassno()
    1
    >>> pari(-23).qfbclassno()
    3
    >>> pari(-104).qfbclassno()
    6
    >>> pari(109).qfbclassno()
    1
    >>> pari(10001).qfbclassno()
    16
    >>> pari(10001).qfbclassno(flag=1)
    16
    >>> pari(3).qfbclassno()
    Traceback (most recent call last):
    ...
    PariError: domain error in classno2: disc % 4 > 1
    >>> pari(4).qfbclassno()
    Traceback (most recent call last):
    ...
    PariError: domain error in classno2: issquare(disc) = 1

    >>> pari(-4).quadclassunit()
    [1, [], [], 1]
    >>> pari(-23).quadclassunit()
    [3, [3], [Qfb(2, 1, 3)], 1]
    >>> pari(-104).quadclassunit()
    [6, [6], [Qfb(5, -4, 6)], 1]
    >>> pari(109).quadclassunit()
    [1, [], [], 5.56453508676047]
    >>> pari(10001).quadclassunit() # random generators
    [16, [16], [Qfb(5, 99, -10, 0.E-19)], 5.29834236561059]
    >>> pari(10001).quadclassunit()[0]
    16
    >>> pari(10001).quadclassunit()[1]
    [16]
    >>> pari(10001).quadclassunit()[3]
    5.29834236561059
    >>> pari(3).quadclassunit()
    Traceback (most recent call last):
    ...
    PariError: domain error in Buchquad: disc % 4 > 1
    >>> pari(4).quadclassunit()
    Traceback (most recent call last):
    ...
    PariError: domain error in Buchquad: issquare(disc) = 1

General number fields::

    >>> K = pari('a^2 - 1/8').nfinit()
    >>> K.nffactor(pari('x^2 - 2'))
    [x + Mod(-a, a^2 - 2), 1; x + Mod(a, a^2 - 2), 1]

    >>> D = pari(-23)
    >>> k = D.quadpoly().nfinit()
    >>> p = k.idealprimedec(3)[0]
    >>> K = D.quadpoly().bnfinit()
    >>> K.bnrclassno(p)
    3

    >>> P = pari('x^6 + 108')
    >>> G = P.galoisinit()
    >>> G[0] == P
    True
    >>> import sys
    >>> if sys.version_info.major > 2: from functools import reduce
    ...
    >>> prod = lambda v: reduce(lambda x,y: x*y, v)
    >>> len(G[5]) == prod(G[7])
    True

    >>> G = pari('x^6 + 108').galoisinit()
    >>> G.galoispermtopol(G[5])
    [x, 1/12*x^4 - 1/2*x, -1/12*x^4 - 1/2*x, 1/12*x^4 + 1/2*x, -1/12*x^4 + 1/2*x, -x]
    >>> G.galoispermtopol(G[5][1])
    1/12*x^4 - 1/2*x
    >>> G.galoispermtopol(G[5][1:4])
    [1/12*x^4 - 1/2*x, -1/12*x^4 - 1/2*x, 1/12*x^4 + 1/2*x]

    >>> G = pari('x^4 + 1').galoisinit()
    >>> G.galoisfixedfield(G[5][1], flag=2)
    [y^2 - 2, Mod(-x^3 + x, x^4 + 1), [x^2 - y*x + 1, x^2 + y*x + 1]]
    >>> G.galoisfixedfield(G[5][5:7])
    [x^4 + 1, Mod(x, x^4 + 1)]
    >>> L = G.galoissubgroups()
    >>> G.galoisfixedfield(L[3], flag=2, v='z')
    [z^2 + 2, Mod(x^3 + x, x^4 + 1), [x^2 - z*x - 1, x^2 + z*x - 1]]

    >>> G = pari('x^6 + 108').galoisinit()
    >>> L = G.galoissubgroups()
    >>> list(L[0][1]) == [3, 2]
    True

    >>> G = pari('x^6 + 108').galoisinit()
    >>> G.galoisisabelian()
    0
    >>> H = G.galoissubgroups()[2]
    >>> H.galoisisabelian()
    Mat(2)
    >>> H.galoisisabelian(flag=1)
    1

    >>> G = pari('x^6 + 108').galoisinit()
    >>> L = G.galoissubgroups()
    >>> G.galoisisnormal(L[0]) == 1
    True
    >>> G.galoisisnormal(L[2]) == 0
    True

    >>> nf = pari('y^2 - 5').nfinit()
    >>> P = nf.idealprimedec(5)[0]
    >>> Q = nf.idealprimedec(2)[0]
    >>> moduli = pari.matrix(2,2,[P,4,Q,4])
    >>> residues = pari.vector(2,[0,1])
    >>> v = nf.idealchinese(moduli,residues)
    >>> b = v + 0*nf.nfgenerator()
    >>> nf.idealval(b, P)
    4
    >>> nf.idealval(b-1, Q)
    4

    >>> nf = pari('x^3 - 2').nfinit()
    >>> x = pari('[2, -2, 2]~')
    >>> y = pari('[4, -4, 4]~')
    >>> nf.idealcoprime(x, y)
    [1/6, 1/6, 0]~

    >>> y = pari('[2, -2, 4]~')
    >>> nf.idealcoprime(x, y)
    [-1/2, 0, 1/2]~

    >>> K = pari('x^2 + 1').nfinit()
    >>> L = K.ideallist(100)
    >>> L[0]   # One ideal of norm 1.
    [[1, 0; 0, 1]]
    >>> L[64]  # 4 ideals of norm 65.
    [[65, 8; 0, 1], [65, 47; 0, 1], [65, 18; 0, 1], [65, 57; 0, 1]]

     >>> nf = pari('x^3-2').nfinit()
    >>> I = pari('[1, -1, 2]~')
    >>> bid = nf.idealstar(I)
    >>> nf.ideallog(5, bid)
    [25]~

     >>> K = pari('x^2 + 1').nfinit()
    >>> F = K.idealprimedec(5); F
    [[5, [-2, 1]~, 1, 1, [2, -1; 1, 2]], [5, [2, 1]~, 1, 1, [-2, -1; 1, -2]]]
    >>> F[0].pr_get_p()
    5

     >>> nf = pari('x^3 - 2').nfinit()
    >>> I = pari('[1, -1, 2]~')
    >>> nf.idealstar(I)
    [[[43, 9, 5; 0, 1, 0; 0, 0, 1], [0]], [42, [42]], [Mat([[43, [9, 1, 0]~, 1, 1, [-5, 2, -18; -9, -5, 2; 1, -9, -5]], 1]), Mat([[43, [9, 1, 0]~, 1, 1, [-5, 2, -18; -9, -5, 2; 1, -9, -5]], 1])], [[[[42], [3], [43, 9, 5; 0, 1, 0; 0, 0, 1], [[[-14, -8, 20]~, [1, 34, 38], [43, [9, 1, 0]~, 1, 1, [-5, 2, -18; -9, -5, 2; 1, -9, -5]]]~, 3, [42, [2, 1; 3, 1; 7, 1]]]]], [[], Vecsmall([])]], [Mat(1)]]

     >>> Kpari = pari('y^3 - 17').nfinit()
    >>> Kpari.getattr('zk')
    [1, 1/3*y^2 - 1/3*y + 1/3, y]
    >>> Kpari.nfbasistoalg(42)
    Mod(42, y^3 - 17)
    >>> Kpari.nfbasistoalg("[3/2, -5, 0]~")
    Mod(-5/3*y^2 + 5/3*y - 1/6, y^3 - 17)
    >>> Kpari.getattr('zk') * pari("[3/2, -5, 0]~")
    -5/3*y^2 + 5/3*y - 1/6

    >>> k = pari('x^2 + 5').nfinit()
    >>> a = k.nfgenerator()
    >>> x = 10
    >>> y = a + 1
    >>> k.nfeltdiveuc(x, y)
    [2, -2]~

    >>> x = pari('x')
    >>> kp = pari('x^2 + 5').nfinit()
    >>> I = kp.idealhnf(x)
    >>> kp.nfeltreduce(12, I)
    [2, 0]~
    >>> z = pari('[12, 0]~') - kp.nfeltreduce(12, I)
    >>> I.matinverseimage(z) != pari('[]~')
    True

    >>> nf = pari('x^2 + 2').nfinit()
    >>> nf.nfgaloisconj()
    [-x, x]~
    >>> nf = pari('x^3 + 2').nfinit()
    >>> nf.nfgaloisconj()
    [x]~
    >>> nf = pari('x^4 + 2').nfinit()
    >>> nf.nfgaloisconj()
    [-x, x]~

    >>> K = pari('t^3 - t + 1').nfinit()
    >>> t = pari('t')
    >>> K.nfhilbert(t, t + 2) == -1
    True
    >>> P = K.idealprimedec(5)[0]   # Prime ideal above 5
    >>> pari(K).nfhilbert(t, t + 2, P) == -1
    True
    >>> P = K.idealprimedec(23)[0] # Prime ideal above 23, ramified
    >>> pari(K).nfhilbert(t, t + 2, P) == 1
    True

    >>> Fp = pari('a^2-a-1').nfinit()
    >>> a = pari('a')
    >>> A = pari('[1,2,a,3; 3,0,a+2,0; 0,0,a,2; 3+a,a,0,1]')
    >>> I = [Fp.nfalgtobasis(-2*a+1), Fp.nfalgtobasis(7), Fp.nfalgtobasis(3), Fp.nfalgtobasis(1)]
    >>> Fp.nfhnf([A, I])
    [[1, [-969/5, -1/15]~, [15, -2]~, [-1938, -3]~; 0, 1, 0, 0; 0, 0, 1, 0; 0, 0, 0, 1], [[3997, 1911; 0, 7], [15, 6; 0, 3], 1, [1, 0]~]]
    >>> Kp = pari('b^3-2').nfinit()
    >>> b = pari('b')
    >>> A = pari('[1,0,0,5*b; 1,2*b^2,b,57; 0,2,1,b^2-3; 2,0,0,b]')
    >>> I = [Kp.nfalgtobasis(2), Kp.nfalgtobasis(b**2+3), Kp.nfalgtobasis(1), Kp.nfalgtobasis(1)] 
    >>> Kp.nfhnf([A, I])
    [[1, -225, 72, -31; 0, 1, [0, -1, 0]~, [0, 0, -1/2]~; 0, 0, 1, [0, 0, -1/2]~; 0, 0, 0, 1], [[1116, 756, 612; 0, 18, 0; 0, 0, 18], 2, [1, 0, 0]~, [2, 0, 0; 0, 1, 0; 0, 0, 1]]]
    >>> Kp = pari('b^2+5').nfinit()
    >>> A = pari('[1,0,0,5*b; 1,2*b^2,b,57; 0,2,1,b^2-3; 2,0,0,b]')
    >>> I = [Kp.nfalgtobasis(2), Kp.nfalgtobasis(3+b**2), Kp.nfalgtobasis(1), Kp.nfalgtobasis(1)]
    >>> Kp.nfhnf([A,I])
    [[1, [15, 6]~, [0, -54]~, [113, 72]~; 0, 1, [-4, -1]~, [0, -1]~; 0, 0, 1, 0; 0, 0, 0, 1], [[360, 180; 0, 180], [6, 4; 0, 2], [1, 0]~, 1]]
    >>> A = pari('[1,0,0,5*b; 1,2*b,b,57; 0,2,1,b-3; 2,0,b,b]')
    >>> I = [Kp.idealprimedec(2)[0][1],Kp.nfalgtobasis(3+b),Kp.nfalgtobasis(1),Kp.nfalgtobasis(1)]
    >>> Kp.nfhnf([A, I])
    [[1, [7605, 4]~, [-8110, -51]~, [2313, 50]~; 0, 1, 0, -1; 0, 0, 1, 0; 0, 0, 0, 1], [[19320, 2520; 0, 168], [2, 1; 0, 1], 1, 1]]
    >>> pari('x^3 - 17').nfinit()
    [x^3 - 17, [1, 1], -867, 3, [[1, 1.68006914259990, 2.57128159065824; 1, -0.340034571299952 - 2.65083754153991*I, -1.28564079532912 + 2.22679517779329*I], [1, 1.68006914259990, 2.57128159065824; 1, -2.99087211283986, 0.941154382464174; 1, 2.31080297023995, -3.51243597312241], [16, 27, 41; 16, -48, 15; 16, 37, -56], [3, 1, 0; 1, -11, 17; 0, 17, 0], [51, 0, 16; 0, 17, 3; 0, 0, 1], [17, 0, -1; 0, 0, 3; -1, 3, 2], [51, [-17, 6, -1; 0, -18, 3; 1, 0, -16]], [3, 17]], [2.57128159065824, -1.28564079532912 + 2.22679517779329*I], [3, x^2 - x + 1, 3*x], [1, 0, -1; 0, 0, 3; 0, 1, 1], [1, 0, 0, 0, -4, 6, 0, 6, -1; 0, 1, 0, 1, 1, -1, 0, -1, 3; 0, 0, 1, 0, 2, 0, 1, 0, 1]]
    >>> pari('x^2 + 10^100 + 1').nfinit()
    [...]
    >>> pari('1.0').nfinit()
    Traceback (most recent call last):
    ...
    PariError: incorrect type in checknf [please apply nfinit()] (t_REAL)
    >>> F = pari('y^3-2').nfinit()
    >>> G = pari('y^3-2').nfinit()
    >>> F.nfisisom(G)
    [y]
    >>> GG = pari('y^3-4').nfinit()
    >>> F.nfisisom(GG)
    [1/2*y^2]
    >>> F.nfisisom(GG)
    [1/2*y^2]
    >>> F.nfisisom(GG[0])
    [1/2*y^2]
    >>> H = pari('y^2-2').nfinit()
    >>> F.nfisisom(H)
    0
    >>> K = pari('y^2 + y + 1').nfinit()
    >>> L = pari('y^2 + 3').nfinit()
    >>> K.nfisisom(L)
    [-1/2*y - 1/2, 1/2*y - 1/2]

    >>> pari('x^2 + 1').nfbasis()
    [1, x]
    >>> pari('y^2 + y + 1').nfbasis()
    [1, y]
    >>> pari('x^3 - 17').nfbasis()
    [1, x, 1/3*x^2 - 1/3*x + 1/3]
    >>> pari('x^4 + 13*x^2 -12*x + 52').nfbasis()
    [1, x, x^2, 1/12*x^3 - 1/6*x^2 + 5/12*x + 1/6]

    >>> K = pari('y^3 - 250').nfinit()
    >>> P = K.idealprimedec(5)[1]
    >>> modP = K.nfmodprinit(P)
    >>> zk = K.nf_get_zk(); zk
    [1, 1/5*y, 1/25*y^2]
    >>> mods = [K.nfmodpr(t, modP) for t in zk]; mods
    [1, y, 2*y + 1]
    >>> lifts = [K.nfbasistoalg_lift(K.nfmodprlift(x, modP)) for x in mods]; lifts
    [1, 1/5*y, 2/5*y + 1]
    >>> K.nfeltval(lifts[2] - zk[2], P) == 1
    True

    # Logarithmic l-class groups (bnflog.c)
    >>> K = pari('x^2 + 521951').bnfinit()
    >>> K.bnflog(2)
    [[4, 2], [4], [2]]
    >>> K = pari('x^4 + 13*x^2 -12*x + 52').bnfinit()
    >>> K.bnflog(2)
    [[], [], []]
    >>> K.bnflog(3)
    [[3], [3], []]
    >>> K.bnflog(7)
    [[7], [], [7]]
    >>> K = pari('y^6 - 3*y^5 + 5*y^3 - 3*y + 1').nfinit()
    >>> K.bnflogef(K.idealprimedec(2)[0])
    [6, 1]
    >>> K.bnflogef(K.idealprimedec(5)[0])
    [1, 2]
    >>> K.bnflogdegree(K.idealprimedec(5)[0], 5)
    36
    >>> K.bnflogdegree(K.idealprimedec(5)[0], 7)
    25
    >>> K = pari('y^2 + 1').nfinit()
    >>> P = K.idealprimedec(2)[0]        # the ramified prime above 2
    >>> K.nfislocalpower(P, -1, 2) == 1   # -1 is a square
    True
    >>> K.nfislocalpower(P, -1, 4) == 0   # but not a 4th power
    True
    >>> K.nfislocalpower(P, 2, 2) == 0    # and 2 is not a square
    True
    >>> Q = K.idealprimedec(5)[0]     # some prime above 5
    >>> K.nfislocalpower(Q, pari('[0, 32]~'), 30)  == 1 # 32*I is locally a 30th power
    True
    >>> K = pari('y^2 + y + 1').nfinit()
    >>> L = K.rnfinit(pari('x^3 - y')) # = K(zeta_9), globally cyclotomic
    >>> L.rnfislocalcyclo() == 1
    True

    # We expect 3-adic continuity by Krasner's lemma
    >>> [int(K.rnfinit(pari('x^3 - y + 3^%d'%i)).rnfislocalcyclo()) for i in range(1,6)]
    [0, 1, 1, 1, 1]

# Sums
    >>> pari('n').sumformal()
    1/2*n^2 + 1/2*n
    >>> f = pari('n -> n^3 + n^2 + 1')
    >>> f('n').sumformal()
    1/4*n^4 + 5/6*n^3 + 3/4*n^2 + 7/6*n
    >>> pari('n').sumformal()
    1/2*n^2 + 1/2*n
    >>> f = pari('n -> n^3 + n^2 + 1')
    >>> F = f('n').sumformal(); F
    1/4*n^4 + 5/6*n^3 + 3/4*n^2 + 7/6*n
    >>> sum([f(n) for n in range(1001, 2001)]) == F.subst('n', 2000) - F.subst('n', 1000)
    True
    >>> pari('x^2 + x*y + y^2').sumformal('y')
    y*x^2 + (1/2*y^2 + 1/2*y)*x + (1/3*y^3 + 1/2*y^2 + 1/6*y)
    >>> S = pari('x^2 + x*y + y^2').sumformal('y'); S
    y*x^2 + (1/2*y^2 + 1/2*y)*x + (1/3*y^3 + 1/2*y^2 + 1/6*y)
    >>> x = pari('x'); y = pari('y')
    >>> x**2 * y + x*y.sumformal() + (y**2).sumformal() == S
    True

    # NOTE: in Pari 2.9.1 idealstar(,N) is not the same as pari('x').nfinit().idealstar(N)
    >>> G = pari(8).znstar(1)  # flag 1 means to compute generators
    >>> CHARS = [1,3,5,7]
    >>> [G.znchartokronecker(n) for n in CHARS]
    [4, -8, 8, -4]
    >>> [G.znchartokronecker(n,1) for n in CHARS]
    [1, -8, 8, -4]

    # Pari orders variables by creation time.  The
    # ordering determines whether xy is an element
    # of Q[x][y] or Q[y][x].
    # Newer elements have lower priority.  Lower priority
    # elements are in coefficients.  The highest priority
    # variable is the main variable of a polynomial.
    # The nfroots method requires that the variable used
    # in defining the number field have lower priority
    # than the variable of the polynomial.
    >>> y = pari('y') 
    >>> x = pari('zz') # this one will have lower priority
    >>> nf = pari(x**2 + 2).nfinit()
    >>> nf.nfroots(y**2 + 2)
    [Mod(-zz, zz^2 + 2), Mod(zz, zz^2 + 2)]
    >>> nf = pari(x**3 + 2).nfinit()
    >>> nf.nfroots(y**3 + 2)
    [Mod(zz, zz^3 + 2)]
    >>> nf = pari(x**4 + 2).nfinit()
    >>> nf.nfroots(y**4 + 2)
    [Mod(-zz, zz^4 + 2), Mod(zz, zz^4 + 2)]

    >>> nf = pari('x^2 + 1').nfinit()
    >>> [nf.nfbasistoalg_lift(r) for r in nf.nfrootsof1()]
    [4, x]

    >>> x = pari('xx1'); x
    xx1
    >>> y = pari('yy1'); y
    yy1
    >>> nf = pari(y**2 - 6*y + 24).nfinit()
    >>> rnf = nf.rnfinit(x**2 - y)
    >>> P = pari('[[[1, 0]~, [0, 0]~; [0, 0]~, [1, 0]~], [[2, 0; 0, 2], [2, 0; 0, 1/2]]]')
    >>> rnf.rnfidealdown(P)
    2

    >>> f = pari('y^3+y+1')
    >>> K = f.nfinit()
    >>> x = pari('x'); y = pari('y')
    >>> g = x**5 - x**2 + y
    >>> L = K.rnfinit(g)

     >>> pari(-23).quadhilbert()
     x^3 - x^2 + 1

     >>> pari(145).quadhilbert()
     x^4 - x^3 - 5*x^2 - x + 1
     >>> pari(-12).quadhilbert()   # Not fundamental
     Traceback (most recent call last):
     ...
     PariError: domain error in quadray: isfundamental(D) = 0

    # Closures

    >>> def the_answer():
    ...     return 42
    >>> f = pari(the_answer)
    >>> f()
    42

    >>> cube = pari(lambda i: i**3)
    >>> cube.apply(range(10))
    [0, 1, 8, 27, 64, 125, 216, 343, 512, 729]

"""

