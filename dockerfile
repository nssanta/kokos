FROM python:3.11.5
COPY requirements.txt ./requirements.txt
COPY nApi.py ./nApi.py
COPY TextAnalyst.py ./TextAnalyst.py
COPY WebParserS.py ./WebParserS.py
COPY nT.json ./nT.json
RUN pip install -r requirements.txt
CMD ["python", "./nApi.py"]
