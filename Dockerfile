FROM python:2.7

RUN apt-get -y update \
    && apt-get install -y libqt4-dev cmake xvfb

COPY . /sharppy

WORKDIR /sharppy
RUN pip install numpy pyside==1.2.4
RUN python setup.py install

WORKDIR /sharppy/runsharp
CMD python full_gui.py
