cmake_minimum_required(VERSION 3.8)
project(line_follower_bot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    launch
    urdf
    rviz
    worlds
    meshes
  DESTINATION
    share/${PROJECT_NAME}
)
install(
  DIRECTORY
    launch
    urdf
    worlds
    meshes
    rviz
  DESTINATION
    share/${PROJECT_NAME}
)
ament_package()
