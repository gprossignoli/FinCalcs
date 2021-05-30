FROM python:3.9-buster

RUN apt-get -y update

EXPOSE 8001

RUN useradd --create-home fincalcsuser

WORKDIR /home/fincalcsuser/fincalcs

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py  .
COPY settings.ini .
RUN touch fincalcs.log fincalcs_errors.log
COPY src ./src

RUN chown -R fincalcsuser .
RUN chmod -R 700 .

USER fincalcsuser

ENTRYPOINT ["python", "main.py"]