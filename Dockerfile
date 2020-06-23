FROM python:3.7
COPY /app /app
WORKDIR /app
COPY app/boka_tools-0.0.4-py3-none-any.whl ./boka_tools-0.0.4-py3-none-any.whl
RUN apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin python3.7-dev
RUN apt-get install unixodbc-dev
RUN pip3 install -r requirements.txt
EXPOSE 8501
CMD streamlit run app.py