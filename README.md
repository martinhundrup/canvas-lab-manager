# Canvas Lab Manager
Developed by Christopher Pereyda for WSU.

# Installation
### Python
1. Install python3.10
```commandline
apt-get install python3.10
```

### MOSS
1. To obtain a Moss account, send a mail message to moss@moss.stanford.edu. The body of the message should appear exactly as follows:
```commandline
registeruser
mail username@domain
```
where *username@domain* is your email address.

2. Place the moss file in the project base with the moss file sent via email.

3. Install pearl
```commandline
curl -L http://xrl.us/installperlnix | bash
```

### Canvas API Key
1. Navigate to your institution's canvas site.
2. Click your account then settings.
3. Scroll down to New Access Token, click and follow directions.
   1. We recommend limiting a key to one term or shorter.
4. Save this key in a secure place (This program does not save your key).

### Python Libraries
1. Install Tkinter
```commandline
apt-get install python3-tk
```

2. Install others
```commandline
pip install canvasapi pandas numpy py7zr matplotlib seaborn beautifulsoup4 networkx
```

# Running
1. Execute the following command
```commandline
python main.py
```