# coding=utf-8
import pytest


@pytest.fixture
def global_paths():
    pytest.dat_path = "./datum/"
    pytest.sh_path = pytest.dat_path + "sh/"
    pytest.sz_path = pytest.dat_path + "sz/"
    pytest.daily_path = pytest.sz_path + "lday/"
    pytest.min_path = pytest.sz_path + "minline/"

    pytest.jjw_min_file = pytest.min_path + "sz300474" + "lc1"

    sz_min_path = "./datum/sz/minline/"
    pytest.byd_minsfile = sz_min_path + "sz002594.lc1"



