/*
py_canupo.cpp: wrap CANUPO libraries into a python interface using
Boost.Python.

Zhan Li <zhanli1986@gmail.com>
 */

#include "py_canupo.hpp"

// // write a class of integer that can be passed by reference
// struct RefInt
// {
//   RefInt(int val) { m_val=val; }
//   int m_val;
//   void set_value(int val) { m_val=val; }
//   int get_value() { return m_val; }
// };

// // write a wrapper function for read_msc_header, as Python does NOT support passing by reference 
// int py_read_msc_header(MSCFile& mscfile, std::vector<FloatType>& scales, RefInt& nparams)
// {
//   int ptnparams, npts;
//   npts = read_msc_header(mscfile, scales, ptnparams);
//   nparams.set_value(ptnparams);
//   return npts;
// }

bp::tuple py_read_msc_header(MSCFile& mscfile)
{
  int ptnparams, npts;
  std::vector<FloatType> scales;
  npts = read_msc_header(mscfile, scales, ptnparams);

  bp::list py_scales;
  for(std::size_t i=0; i<scales.size(); i++)
  {
    py_scales.append(scales[i]);
  }
  // std::for_each(scales.begin(), scales.end(), py_scales.append);
  return bp::make_tuple(npts, py_scales, ptnparams);
}

void py_read_msc_data(MSCFile& mscfile, int nscales, int npts, std::vector<FloatType>& data, int nparams, bool convert_from_tri_to_2D=false)
{
  data.clear();
  std::size_t ndata = npts*nscales*2;
  data.resize(ndata);
  read_msc_data(mscfile, nscales, npts, data.data(), nparams, convert_from_tri_to_2D);
}

py_MSCFile::py_MSCFile(const char* name)
  : MSCFile(name)
{
  npts = read_header(scales, ptnparams);
  nscales = scales.size();
  param.resize(ptnparams);
  data.resize(nscales*2);

  // try reading one point and find out the length of a point in the msc file.
  // read all attributes of one point in msc file
  for (int i=0; i<ptnparams; ++i)
  {
      read(param[i]);
  }
  for (int s=0; s<nscales; ++s)
  {
      read(data[s*2]);
      read(data[s*2+1]);
  }
  // we do not care for number of neighbors and average dist between nearest neighbors
  for (int i=0; i<nscales; ++i) read(fooi);

  bp::list py_param, py_data1, py_data2;
  for(std::size_t i=0; i<param.size(); i++)
  {
    py_param.append(param[i]);
  }
  for(std::size_t i=0; i<nscales; i++)
  {
    py_data1.append(data[i*2]);
    py_data2.append(data[i*2+1]);
  }

  this->point_data_len = this->offset - this->data_start_pos;
  this->seekg(this->data_start_pos);
}

bp::tuple py_MSCFile::py_get_header()
{
  bp::list py_scales;
  for(std::size_t i=0; i<scales.size(); i++)
  {
    py_scales.append(scales[i]);
  }
  // std::for_each(scales.begin(), scales.end(), py_scales.append);
  return bp::make_tuple(npts, py_scales, ptnparams);
}

bp::tuple py_MSCFile::py_read_point(size_t pt_idx=std::numeric_limits<size_t>::max(), bool convert_from_tri_to_2D = false)
{
  if (pt_idx == std::numeric_limits<size_t>::max())
  {
    pt_idx = this->next_pt_idx;
  }
  if (pt_idx >= npts)
  {
    std::cerr << "The given index of a point "<< pt_idx << " is out of boundary! Number of points = " << npts << std::endl;
    return bp::make_tuple(bp::object());
  }

  this->seekg(this->data_start_pos+this->point_data_len*pt_idx);
  
  // read all attributes of one point in msc file
  for (int i=0; i<ptnparams; ++i)
  {
      read(param[i]);
  }
  for (int s=0; s<nscales; ++s)
  {
      read(data[s*2]);
      read(data[s*2+1]);
      if (convert_from_tri_to_2D)
      {
          FloatType c = 1 - data[s*2] - data[s*2+1];
          FloatType x = data[s*2+1] + c / 2;
          FloatType y = c * sqrt(3)/2;
          data[s*2] = x;
          data[s*2+1] = y;
      }
  }
  // we do not care for number of neighbors and average dist between nearest neighbors
  for (int i=0; i<nscales; ++i) read(fooi);

  bp::list py_param, py_data1, py_data2;
  for(std::size_t i=0; i<param.size(); i++)
  {
    py_param.append(param[i]);
  }
  for(std::size_t i=0; i<nscales; i++)
  {
    py_data1.append(data[i*2]);
    py_data2.append(data[i*2+1]);
  }

  this->next_pt_idx = pt_idx + 1;
  return bp::make_tuple(py_param, py_data1, py_data2);
}

int py_MSCFile::read_header(std::vector<FloatType>& scales, int& ptnparams)
{
    using namespace std;
    int npts;
    read(npts);
    if (npts<=0)
    {
        cerr << "invalid msc file (negative or null number of points)" << endl;
        exit(1);
    }
    
    int nscales_thisfile;
    read(nscales_thisfile);
    if (nscales_thisfile<=0) {
        cerr << "invalid msc file (negative or null number of scales)" << endl;
        exit(1);
    }
#ifndef MAX_SCALES_IN_MSC_FILE
#define MAX_SCALES_IN_MSC_FILE 1000000
#endif
    if (nscales_thisfile>MAX_SCALES_IN_MSC_FILE) {
        cerr << "This msc file claims to contain more than " << MAX_SCALES_IN_MSC_FILE << " scales. Aborting, this is probably a mistake. If not, simply recompile with a different value for MAX_SCALES_IN_MSC_FILE." << endl;
        exit(1);
    }
    vector<FloatType> scales_thisfile(nscales_thisfile);
    for (int si=0; si<nscales_thisfile; ++si) read(scales_thisfile[si]);

    // all files must be consistant
    if (scales.size() == 0) {
        scales = scales_thisfile;
    } else {
        if (scales.size() != nscales_thisfile) {
            cerr<<"input file mismatch: "<<endl; exit(1);
        }
        for (int si=0; si<scales.size(); ++si) if (!fpeq(scales[si],scales_thisfile[si])) {cerr<<"input file mismatch: "<<endl; exit(1);}
    }
    
    read(ptnparams);

    data_start_pos = offset;

    return npts;
}

//*************************
BOOST_PYTHON_MODULE(canupo)
{
  using namespace boost::python;

  // class_<std::vector<FloatType> >("FloatVec")
  //   .def(vector_indexing_suite<std::vector<FloatType> >())
  //   ;

  // class_<RefInt>("RefInt", init<int>())
  //   .def_readwrite("value", &RefInt::m_val)
  //   ;
  
  class_<py_MSCFile>("MSCFile", init<const char*>())
    .def("get_header", &py_MSCFile::py_get_header)
    .def("read_point", &py_MSCFile::py_read_point, py_MSCFile_py_read_point_overloads())
    .def_readonly("next_pt_idx", &py_MSCFile::next_pt_idx)
    ;

  def("read_msc_header", py_read_msc_header);
  def("read_msc_data", py_read_msc_data, py_read_msc_data_overloads());
}
