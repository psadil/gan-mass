#!/bin/bash

# the docker image must have already been built
# docker build --tag stylegan2ada:latest libs/stylegan2-ada

docker run -it --rm -v `pwd`:/scratch --user $(id -u):$(id -g) \
  stylegan2ada:latest bash -c "(python /scratch/libs/stylegan2-ada/dataset_tool.py  \
  create_from_images /scratch/data/mass512record /scratch/data/mass512)"
  