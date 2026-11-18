#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
export IGN_GAZEBO_RESOURCE_PATH="$DIR/models:$IGN_GAZEBO_RESOURCE_PATH"
ign gazebo -r "$DIR/world/mundo.sdf"