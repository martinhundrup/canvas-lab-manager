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

    terms                                 # Directory to hold data by terms
    ├── Fall_2023                         # Term directory: SEMESTER_YEAR
    │   ├── CPTS_121                      # Directory to hold course data
    │      ├── assignments                # Directory to store downloaded course assigments
    │         ├── assignment_1            # Student submission
    │            ├── TA_1                 # TA directories
    │               ├── student_1         # Student directory
    │                  └── student_code   # Student code dir  
    │               └── ...   
    │            └── ...   
    │         └── ...   
    │      ├── moss_output                # Holds output from moss runs
    │         ├── assignment_1.txt        # Holds moss output for assignment
    │         └── ...   
    │      ├── plagiarism                 # Directory for plagiarism materials
    │         ├── assignment_1.html       # Saved main moss website 
    │         ├── ...                     #     Each asignment has its own file       
    │         ├── course_name.xlsx        # Cheating spreadsheet
    │         └── plots.html              # Directory holding plots for cheating analysis
    │            ├── histogram.png        # Histogram showing distribution of cheating and cutoff mark
    │            └── assignment_1.png     # Connected graph showing cheating groups
    │      ├── grade_book.xlsx            # Grade book for course (check for all required columns) 
    │      ├── late_status.png            # Indicates whether TAs are following late policy
    │      ├── percent_graded.png         # Indicates TAs current grading status 
    │      └── other_files                # Used internally, don't mess with                 
    │   └── ...                           
    └── ...                               
