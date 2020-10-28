新しいマシンで起動する場合

docker build .

（コンテナ内で）

python setup.py build_ext --inplace

後はデータをいい感じに持ってくる（多分どこかのマシンにはあるはず）

実験用コンテナ起動

sudo docker run --gpus all  -it -v `pwd`:/home/ kitazawa/dvr bash

source activate dvr

起動してるコンテナにログイン

sudo docker exec -it