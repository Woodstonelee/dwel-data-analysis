/*
py_canupo.hpp: wrap CANUPO libraries into a python interface using
Boost.Python. Header file for py_canupo.cpp.

Zhan Li <zhanli1986@gmail.com>
Created: Wed Mar 16 15:41:26 EDT 2016
 */

#include <iostream>
#include <limits>
#include "helpers.hpp"

#include <boost/python.hpp>
// #include <boost/python/implicit.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
// #include <boost/foreach.hpp>
#include <boost/shared_ptr.hpp>

namespace bp = boost::python;

bp::tuple py_read_msc_header(MSCFile& mscfile);
void py_read_msc_data(MSCFile& mscfile, int nscales, int npts, std::vector<FloatType>& data, int nparams, bool convert_from_tri_to_2D);
BOOST_PYTHON_FUNCTION_OVERLOADS(py_read_msc_data_overloads, py_read_msc_data, 5, 6)

struct py_MSCFile : MSCFile
{
private:
  int ptnparams, npts; 
  std::vector<FloatType> scales;
  int nscales;
  int read_header(std::vector<FloatType>& scales, int& ptnparams);
  std::vector<FloatType> param;
  std::vector<FloatType> data;
  int fooi;
  size_t data_start_pos;
  size_t point_data_len;

public:
  py_MSCFile(const char* name);
  size_t next_pt_idx=0;
  
  bp::tuple py_get_header();
  bp::tuple py_read_point(size_t pt_idx, bool convert_from_tri_to_2D);  
};
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(py_MSCFile_py_read_point_overloads, py_read_point, 0, 2)
