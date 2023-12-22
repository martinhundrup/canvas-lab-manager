FROM python:3.10.12

# Install pearl
RUN curl -L http://xrl.us/installperlnix | bash

# TKINTER libraries
RUN apt-get update
RUN apt-get install python3-tk -y

# Install pip libraries
ADD docker/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# Add in local files
ADD ./moss ./moss
ADD ./main.py ./main.py
ADD ./util ./util

# Run it 
CMD ["main.py", "docker"]
ENTRYPOINT ["python3"]
