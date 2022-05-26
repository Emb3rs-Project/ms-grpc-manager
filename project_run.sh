LIBSPATH=ms_grpc/plibs

if [ $# -eq 0 ]
  then
    echo "No arguments supplied, Need Path to python.file"
    exit
fi

PYTHONPATH=$PYTHONPATH:$LIBSPATH python $1