ARG TIDYVERSE_TAG

FROM rocker/tidyverse:$TIDYVERSE_TAG

RUN apt-get update \
    && apt-get install -y libpython3-dev python3-venv python3-pip

RUN installGithub.r rstudio/keras@09de409ece8b9a47a4f915ee7397c486fc1e9e91 

ENV PYTHON_PACKAGES="\
    numpy \
    matplotlib \
    pandas \
    tensorflow==2.0 \
    scipy \
    scikit-learn \
    seaborn \
    imutils \
    tabulate \
    nbformat \
    pyemma \
" 

RUN pip3 install --upgrade pip && pip3 install --no-cache-dir $PYTHON_PACKAGES

ENV R_PACKAGES="\
    lime \
    anomalize \
    imputeTS \
    tsoutliers \
    png \
    caret \
" 

RUN install2.r --error $R_PACKAGES