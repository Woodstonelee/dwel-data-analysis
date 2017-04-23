 cmake_minimum_required( VERSION 2.8 )

# set C and C++ compiler explicitly
# has to be before project()
set(CMAKE_C_COMPILER "/usr/local/IT/gcc-4.8.1/bin/gcc")
set(CMAKE_CXX_COMPILER "/usr/local/IT/gcc-4.8.1/bin/g++")

project( CANUPO_Python_Interface )

if(NOT CMAKE_BUILD_TYPE)
 set(CMAKE_BUILD_TYPE "DEBUG")
endif()

# Find necessary packages
# find_package( PythonLibs 2.7 REQUIRED)
# include_directories( ${PYTHON_INCLUDE_DIRS} )
include_directories( "$ENV{HOME}/anaconda_envs/zhanli_py27/include/python2.7" )

MESSAGE( STATUS "CMAKE_MODULE_PATH: " ${CMAKE_MODULE_PATH} )

# find_package( Boost HINTS "/projectnb/echidna/lidar/zhanli86" COMPONENTS python REQUIRED )
# if(Boost_FOUND)
#   include_directories( ${Boost_INCLUDE_DIR} )
# elseif(NOT Boost_FOUND)
#   message(FATAL_ERROR "Unable to find correct Boost version. Did you set BOOST_ROOT?")
# endif()

set(Boost_INCLUDE_DIR "/projectnb/echidna/lidar/zhanli86/lib")
set(Boost_LIBRARIES "/projectnb/echidna/lidar/zhanli86/lib/libboost_python.so")

MESSAGE( STATUS "Boost_INCLUDE_DIR: " ${Boost_INCLUDE_DIR} )
MESSAGE( STATUS "Boost_LIBRARIES: " ${Boost_LIBRARIES} )

# Build the wrapper library
add_definitions("-std=c++11 -std=gnu++11")
add_library( canupo SHARED py_canupo.cpp )
target_link_libraries( canupo ${Boost_LIBRARIES} )

# don't prepend wrapper library name with lib
set_target_properties( canupo PROPERTIES PREFIX "" )
