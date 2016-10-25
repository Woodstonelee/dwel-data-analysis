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
  npts = this->read_header(scales, ptnparams);
  nscales = scales.size();
  param.resize(ptnparams);
  data1.resize(nscales);
  data2.resize(nscales);
  // linenum.resize(1);

  // try reading one point and find out the length of a point in the msc file.
  // read all attributes of one point in msc file
  for (int i=0; i<ptnparams; ++i)
  {
      this->read(param[i]);
  }
  for (int s=0; s<nscales; ++s)
  {
      this->read(data1[s]);
      this->read(data2[s]);
  }
  // we do not care for number of neighbors and average dist between nearest neighbors
  for (int i=0; i<nscales; ++i) this->read(fooi);
  // now read the line number
  // this->read(linenum[0]);

  this->point_data_len = this->offset - this->data_start_pos;
  this->seekg(this->data_start_pos);
}

py_MSCFile::~py_MSCFile()
{
  this->~MSCFile();
  // std::cout << "~py_MSCFile" << std::endl;  
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

bp::tuple py_MSCFile::py_read_point(size_t pts_num=1, size_t pt_idx=std::numeric_limits<size_t>::max(), bool convert_from_tri_to_2D = false)
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

  // set up space to store the data for the pts_num points
  param.resize(ptnparams*pts_num);
  data1.resize(nscales*pts_num);
  data2.resize(nscales*pts_num);
  // linenum.resize(pts_num);

  for (int p=0; p<pts_num; ++p) {
    // read all attributes of one point in msc file
    for (int i=0; i<ptnparams; ++i)
    {
        this->read(param[p*ptnparams + i]);
    }
    for (int s=0; s<nscales; ++s)
    {
        this->read(data1[p*nscales+s]);
        this->read(data2[p*nscales+s]);
        if (convert_from_tri_to_2D)
        {
            FloatType c = 1 - data1[p*nscales+s] - data2[p*nscales+s];
            FloatType x = data2[p*nscales+s] + c / 2;
            FloatType y = c * sqrt(3)/2;
            data1[p*nscales+s] = x;
            data2[p*nscales+s] = y;
        }
    }
    // we do not care for number of neighbors and average dist between nearest neighbors
    for (int i=0; i<nscales; ++i) this->read(fooi);
    // now read the line number
    // this->read(linenum[p]);    
  }
  
  bp::list py_param, py_data1, py_data2, py_linenum;
  for(std::size_t i=0; i<param.size(); i++)
  {
    py_param.append(param[i]);
  }
  for(std::size_t i=0; i<nscales*pts_num; i++)
  {
    py_data1.append(data1[i]);
    py_data2.append(data2[i]);
  }
  // for(std::size_t i=0; i<linenum.size(); i++)
  // {
  //   py_linenum.append(linenum[i]);
  // }

  this->next_pt_idx = pt_idx + pts_num;
  return bp::make_tuple(py_param, py_data1, py_data2);
}

int py_MSCFile::py_read_reset()
{
  this->next_pt_idx = 0;
  this->seekg(this->data_start_pos);
  return 0;
}

int py_MSCFile::read_header(std::vector<FloatType>& scales, int& ptnparams)
{
    using namespace std;
    int npts;
    this->read(npts);
    if (npts<=0)
    {
        cerr << "invalid msc file (negative or null number of points)" << endl;
        exit(1);
    }
    
    int nscales_thisfile;
    this->read(nscales_thisfile);
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
    for (int si=0; si<nscales_thisfile; ++si) this->read(scales_thisfile[si]);

    // all files must be consistant
    if (scales.size() == 0) {
        scales = scales_thisfile;
    } else {
        if (scales.size() != nscales_thisfile) {
            cerr<<"input file mismatch: "<<endl; exit(1);
        }
        for (int si=0; si<scales.size(); ++si) if (!fpeq(scales[si],scales_thisfile[si])) {cerr<<"input file mismatch: "<<endl; exit(1);}
    }
    
    this->read(ptnparams);

    this->data_start_pos = offset;

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
  
  // class_<py_MSCFile>("MSCFile", "Class to read CANUPO MSC file", init<const char*>())
  //   .def("get_header", "Get header (npts, scales, nparam_per_point)", &py_MSCFile::py_get_header)
  //   .def("read_point", "Read MSC data for one point (point_params, msc_data_1, msc_data_2, original_point_index)", &py_MSCFile::py_read_point, py_MSCFile_py_read_point_overloads())
  //   .def_readonly("next_pt_idx", "Index to next point in MSC file", &py_MSCFile::next_pt_idx)
  //   ;

  class_<py_MSCFile>("MSCFile", init<const char*>())
    .def("get_header", &py_MSCFile::py_get_header)
    .def("read_point", &py_MSCFile::py_read_point, py_MSCFile_py_read_point_overloads())
    .def("read_reset", &py_MSCFile::py_read_reset)
    .def_readonly("next_pt_idx", &py_MSCFile::next_pt_idx)
    ;
  
  def("read_msc_header", py_read_msc_header);
  def("read_msc_data", py_read_msc_data, py_read_msc_data_overloads());
}
