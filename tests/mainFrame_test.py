# coding=utf-8
import os
import pytest


# @pytest.fixture
# def global_paths():
    # pytest.dat_path = "./datum/"
    # pytest.sh_path = pytest.dat_path + "sh/"
    # pytest.sz_path = pytest.dat_path + "sz/"
    # pytest.daily_path = pytest.sz_path + "lday/"
    # pytest.min_path = pytest.sz_path + "minline/"

    # pytest.jjw_min_file = pytest.min_path + "sz300474" + "lc1"


def test_jjw_min_file_exist(global_paths):
    os.path.isfile(pytest.jjw_min_file)


def setup_module(module):
    print("setup_module      module:%s" % module.__name__)


def teardown_module(module):
    print("teardown_module   module:%s" % module.__name__)


def setup_function(function):
    print("setup_function    function:%s" % function.__name__)


def teardown_function(function):
    print("teardown_function function:%s" % function.__name__)


# #1. ready soft link the datum to tdx stock clients' dumped files
def test_datum_path_exist():
    path = "./datum/"
    assert os.path.exists(path)


def test_golbal_sh_datum_path_exist1(global_paths):
    assert os.path.exists(pytest.sh_path)


# 1.1  OK, there's no path like ./dat
def test_dat_path_not_exist():
    path = "./dat/"
    assert not os.path.exists(path)


# # 2. We use the daily data and the one minutes, so go down the directories
def test_daily_path_exist(global_paths):

    assert os.path.exists(pytest.daily_path)


def test_min_path_exist(global_paths):
    assert os.path.exists(pytest.min_path)

