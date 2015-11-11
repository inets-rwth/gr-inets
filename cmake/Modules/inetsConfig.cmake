INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_INETS inets)

FIND_PATH(
    INETS_INCLUDE_DIRS
    NAMES inets/api.h
    HINTS $ENV{INETS_DIR}/include
        ${PC_INETS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    INETS_LIBRARIES
    NAMES gnuradio-inets
    HINTS $ENV{INETS_DIR}/lib
        ${PC_INETS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(INETS DEFAULT_MSG INETS_LIBRARIES INETS_INCLUDE_DIRS)
MARK_AS_ADVANCED(INETS_LIBRARIES INETS_INCLUDE_DIRS)

