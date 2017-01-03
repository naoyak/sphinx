# -*- coding: utf-8 -*-
"""
    test_apidoc
    ~~~~~~~~~~~

    Test the sphinx.apidoc module.

    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from __future__ import print_function

from collections import namedtuple

import pytest

from sphinx.apidoc import main as apidoc_main

from util import rootdir, path, remove_unicode_literals


@pytest.fixture()
def apidoc(tmpdir, apidoc_params):
    _, kwargs = apidoc_params
    coderoot = kwargs.get('coderoot', (rootdir / 'root'))
    outdir = path(tmpdir) / 'out'
    args = ['sphinx-apidoc', '-o', outdir, '-F', coderoot] + kwargs.get('options', [])
    apidoc_main(args)
    return namedtuple('apidoc', 'coderoot,outdir')(coderoot, outdir)


@pytest.fixture
def apidoc_params(request):
    markers = request.node.get_marker("apidoc")
    pargs = {}
    kwargs = {}

    if markers is not None:
        for info in reversed(list(markers)):
            for i, a in enumerate(info.args):
                pargs[i] = a
            kwargs.update(info.kwargs)

    args = [pargs[i] for i in sorted(pargs.keys())]
    return args, kwargs


@pytest.mark.apidoc(coderoot=(rootdir / 'root'))
def test_simple(make_app, apidoc):
    outdir = apidoc.outdir
    assert (outdir / 'conf.py').isfile()
    assert (outdir / 'autodoc_fodder.rst').isfile()
    assert (outdir / 'index.rst').isfile()

    app = make_app('text', srcdir=outdir)
    app.build()
    print(app._status.getvalue())
    print(app._warning.getvalue())


@pytest.mark.apidoc(
    coderoot=(rootdir / 'root' / 'pep_0420'),
    options=["--implicit-namespaces"],
)
def test_pep_0420_enabled(make_app, apidoc):
    outdir = apidoc.outdir
    assert (outdir / 'conf.py').isfile()
    assert (outdir / 'a.b.c.rst').isfile()
    assert (outdir / 'a.b.x.rst').isfile()

    with open(outdir / 'a.b.c.rst') as f:
        rst = f.read()
        assert "a.b.c package\n" in rst
        assert "automodule:: a.b.c.d\n" in rst
        assert "automodule:: a.b.c\n" in rst

    with open(outdir / 'a.b.x.rst') as f:
        rst = f.read()
        assert "a.b.x namespace\n" in rst
        assert "automodule:: a.b.x.y\n" in rst
        assert "automodule:: a.b.x\n" not in rst

    app = make_app('text', srcdir=outdir)
    app.build()
    print(app._status.getvalue())
    print(app._warning.getvalue())


@pytest.mark.apidoc(coderoot=(rootdir / 'root' / 'pep_0420'))
def test_pep_0420_disabled(make_app, apidoc):
    outdir = apidoc.outdir
    assert (outdir / 'conf.py').isfile()
    assert not (outdir / 'a.b.c.rst').exists()
    assert not (outdir / 'a.b.x.rst').exists()

    app = make_app('text', srcdir=outdir)
    app.build()
    print(app._status.getvalue())
    print(app._warning.getvalue())


@pytest.mark.apidoc(coderoot=(rootdir / 'root' / 'pep_0420' / 'a' / 'b'))
def test_pep_0420_disabled_top_level_verify(make_app, apidoc):
    outdir = apidoc.outdir
    assert (outdir / 'conf.py').isfile()
    assert (outdir / 'c.rst').isfile()
    assert not (outdir / 'x.rst').exists()

    with open(outdir / 'c.rst') as f:
        rst = f.read()
        assert "c package\n" in rst
        assert "automodule:: c.d\n" in rst
        assert "automodule:: c\n" in rst

    app = make_app('text', srcdir=outdir)
    app.build()
    print(app._status.getvalue())
    print(app._warning.getvalue())


@pytest.mark.apidoc(
    coderoot=(rootdir / 'root'),
    options=[
        '--doc-project', u'プロジェクト名'.encode('utf-8'),
        '--doc-author', u'著者名'.encode('utf-8'),
        '--doc-version', u'バージョン'.encode('utf-8'),
        '--doc-release', u'リリース'.encode('utf-8'),
    ],
)
def test_multibyte_parameters(make_app, apidoc):
    outdir = apidoc.outdir
    assert (outdir / 'conf.py').isfile()
    assert (outdir / 'autodoc_fodder.rst').isfile()
    assert (outdir / 'index.rst').isfile()

    conf_py = (outdir / 'conf.py').text()
    conf_py_ = remove_unicode_literals(conf_py)
    assert u"project = 'プロジェクト名'" in conf_py_
    assert u"author = '著者名'" in conf_py_
    assert u"version = 'バージョン'" in conf_py_
    assert u"release = 'リリース'" in conf_py_

    app = make_app('text', srcdir=outdir)
    app.build()
    print(app._status.getvalue())
    print(app._warning.getvalue())
