# Canvas Lab Manager
Developed by Christopher Pereyda for WSU.

# Setup
### Canvas API Key
1. Navigate to your institution's canvas site.
2. Click your account then settings.
3. Scroll down to New Access Token, click and follow directions.
   1. We recommend limiting a key to one term or shorter.
4. Save this key in a secure place (This program does not save your key).

### MOSS
1. To obtain a Moss account, send a mail message to moss@moss.stanford.edu. The body of the message should appear exactly as follows:
```commandline
registeruser
mail username@domain
```
where *username@domain* is your email address.

2. Place the moss file in the project base with the moss file sent via email.

# Installation - Docker
1. Run the following commands
```commandline
chmod +x docker/run_docker.sh
```

# Installation - Manual
### Python
1. Install python3.10
```commandline
apt-get install python3.10
```
2. Install pearl
```commandline
curl -L http://xrl.us/installperlnix | bash
```

### Python Libraries
1. Install Tkinter
```commandline
apt-get install python3-tk
```

2. Install others
```commandline
pip install canvasapi pandas numpy py7zr matplotlib seaborn beautifulsoup4 networkx openpyxl
```

# Running
### Python 
1. Execute the following command
```commandline
python main.py
```

### Docker
1. Execute the following command
```commandline
docker/run_docker.sh
```

# Data / results
Results can be found in the term directory:
    .
    ├── CPTS_121.zip                 # Class to check through
    │   ├──  john_doe                # TA First name then lest name
    │      ├──  PA1.zip              # PA submission donwloaded from canvas and renamed properly
    │         └──  studentcode.zip   # Student submission
    │      ├── ...                   # Intermeddiate PAs
    │      └── PAn.zip               # Last PA to check
    │   ├──  ...                     # Intermediate TA names
    │   └──  jane_deer               # Last TA name
    │      ├──  PA1.zip              # PA submission donwloaded from canvas and renamed properly
    │         └──  studentcode.zip   # Student submission
    │      ├── ...                   # Intermeddiate PAs
    │      └── PAn.zip               # Last PA to check
    ├── ...                          # Intermeddiate classes
    └── CPTS_122.zip                 # Last class to check
