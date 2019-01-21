"""test model and tag datum functions"""
# coding=utf-8
import os
import sys
import pytest
import pandas as pd
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
from dataStruct import stockdata


class TestStockClass(object):
    def test_data_files_exist(self):
        msg = "File doesn't Exist!!"
        print("\n ===>the absolute directory==>",parentdir)
        assert os.path.exists("./localdata/sh600640.day"), msg
        assert os.path.exists("./localdata/sh600640.lc1"),msg
        assert os.path.exists("./localdata/sh600640.lc5"),msg

    def test_data_files_not_exist(self):
        """test_data_files_not_exist"""
        msg = "File doesn't Exist!!"
        assert not os.path.exists("../localdata/sh600641.day"), msg

    @pytest.fixture
    def min_datum_obj(self):
        '''Returns a stockdata instance '''
        pathfilename = "./localdatai/sh600460.lc1"
        return stockdata.minuteOfStock(pathfilename)

    @pytest.fixture
    def day_datum_obj(self):
        '''Returns a stockdata instance '''
        pathfilename = "./localdata/sh600460.day"
        return stockdata.daysDataOfStock(pathfilename)

    @pytest.mark.parametrize("filename,    expected", [
                           ("sh600460.day",    True),
                           ("sh600460.lc1",    True),
                           ("sh600460.lc5",    True),
                           ("sh600460.lc1",    True)])
    def test_data_files_if_exist(self, filename, expected):
        path = "./localdata/"
        assert os.path.exists(path+filename) == expected

    def test_day_datum_obj_is_DataFrame(self, day_datum_obj):
        df_slw = day_datum_obj.DF
        assert isinstance(df_slw, pd.DataFrame)

    def test_day_datum_obj_Date_Range(self, day_datum_obj):
         date_range= day_datum_obj.getDateRange()
         print("\n ===>the Date Range", date_range)

    def test_day_datum_obj_first_of_DataFrame(self, day_datum_obj):
        first_line = day_datum_obj.DF.iloc[0]
        print("\n ===>the Date Range \n", first_line)
        assert isinstance(first_line, pd.Series)

if __name__ == "__main__":
    pytest.main("-s tests/test_tag_minutes_series.py")
    #  pytest.main("-sv tests/test_tag_minutes_series.py")
    # pytest.main()  # 遍历相同目录下的所以test开头的用例
    # pytest.main("-q test_main.py")  # 指定测试文件
    # pytest.main("/root/Documents/python3_1000/1000/python3_pytest")  # 指定测试目录

