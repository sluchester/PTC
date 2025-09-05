cmake_minimum_required(VERSION 3.22)
project(Serialemu)

set(CMAKE_CXX_STANDARD 14)

add_executable(serialemu main.cpp Canal.cpp Argparse.cpp Pts.cpp)

target_link_libraries(serialemu pthread util)