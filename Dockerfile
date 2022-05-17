FROM python:3
EXPOSE 8501

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . . 

ENTRYPOINT ["streamlit", "run"]
CMD [ "streamlit_test.py" ]