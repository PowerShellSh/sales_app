
# python version number:3.11
FROM python:3.11

# code ... directory for python codes.
WORKDIR /code

# copy localcode to container image.
COPY ./code /code

# upgrade pip command
RUN pip install --upgrade pip

# install python lib
RUN pip install -r requirements.txt
