FROM kundajelab/cuda-anaconda-base

COPY .  /home

WORKDIR /home

RUN conda env create -f environment.yaml