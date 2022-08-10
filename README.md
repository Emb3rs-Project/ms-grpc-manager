# Module System gRPC - Manager 
Module System responsible to manage simulations.

## Git
Clone this repository:
```shell
git clone https://github.com/Emb3rs-Project/ms-grpc-manager.git
```

Load submodules:
```shell
git submodule init
git submodule update
```

## Setup Local Environment
Create Conda environment and install packages:
```shell
conda env create -n ms-grpc-manager -f environment-py39.yml
conda activate ms-grpc-manager
```

Create environment variables config file:
```shell
cp .env.example .env
```

Run grpc server:
```shell
PYTHONPATH=$PYTHONPATH:ms-grpc/plibs:module python server.py
```

## Setup Docker Environment
Create environment variables config file:
```shell
cp .env.example .env
```

Build docker image:
```shell
DOCKER_BUILDKIT=1 docker build -t ms-grpc-manager .
```

Run docker image:
```shell
docker run -p 50041:50041 --name ms-grpc-manager --rm ms-grpc-manager
```

**NOTE**: *If you've run docker-dev from the Emb3rs-project repository before, I advise use the embers network 
in docker run to access PGSQL and change the database settings inside .env to Platform DB.*  

Run docker image with embers network:
```shell
docker run -p 50041:50041 --network dev_embers --name ms-grpc-manager --rm ms-grpc-manager
```