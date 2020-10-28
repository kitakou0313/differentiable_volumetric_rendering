新しいマシンで起動する場合

docker build .

（コンテナ内で）

python setup.py build_ext --inplace

実験用コンテナ起動

sudo docker run --gpus all  -it -v `pwd`:/home/ kitazawa/dvr bash

source activate dvr