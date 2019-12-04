# Docker image for Sublime Text UnitTesting


## From Docker Hub
```sh
# cd to package
docker run --rm -it -e PACKAGE=$PACKAGE -v $PWD:/project sublimetext/unittesting 
```

## Build image from scratch
```sh
# cd to UnitTesting/docker
docker build -t unittesting .
# cd to package
docker run --rm -it -e PACKAGE=$PACKAGE -v $PWD:/project unittesting 
```
