# ScoreComparisonTool
This is the score comparison tool RAP process folder. It includes everything needed to produce the Score Comparison Tool File for the PROMs publication.

## Set up
1. Download git from the software center (if it does not appear raise a resolveIT)
2. In your Command Prompt App, navigate to the folder where you want to keep the score comparison tool (if you do not know how to do this, look at this website: https://www.lifewire.com/change-directories-in-command-prompt-5185508)
3. Copy the link for this repository from gitlab and type `git clone {URL}` in your command prompt.
4. Now when you navigate to that folder, the Score Comparison Tool folder should appear.
5. If you do not have Visual Studio Code (or another python compiler) installed, download it from the software center and request a python installation from ResolveIT. Do not go on to step 6 before getting this.
6. Go into the commandPrompt app and type the following commands pressing enter between each line: 
```
python -m pip install --user --upgrade pip
python -m pip install --user numpy
python -m pip install openpyxl
python -m pip install pandas
python -m pip install --user --upgrade pandas
python -m pip install pyodbc
```
7. Open the whole folder in Visual Studio by opening visual studio, clicking 'File' then clicking 'Open Folder...' and selecting the score comparison tool folder. 
8. Do Ctrl+Shift+X and install the Python extension.

## Parameter Definitions
The following list describes what the different parameters are that require changing for the new publication method.

**FYEAR** - First year of the financial year of this publication (e.g. if this is a publication for data from the financial year 2019-2020 FYEAR will be '2019')

**FROM_DATE** - starting date for the data you want to look at (usually the start date of the financial year i.e. the 1st of April)

**TO** - final date of the data you want to look at (last day of the financial year usually)

**TABLE** - suffix of the most recent data table for the financial year you are working on.

**AGG_METHOD** - aggregation method, is it additive or not?

**PUBLICATION_DATE** - date that you are hoping to publish on

**PUBLICATION_LINK** - link at which the publication can be found

**PROV_PUBLICATION** - true if the publication is the provisional publication, false if it is the final annual publication

**DATE_FINALIZED_PUBLICATION** - month and year when the final publication will get published

**PUB_FILE_NAME** - Name that you would like the Score Comparison Tool file to have once produced. Please leave it as an xlsx extension.

## Running the Code 
In order to set the variables (dates, tables etc.) needed for the new publication, go into the `PROMSconfig.py` file and change the variables as instructed. This is the only thing that should need changing if nothing about the fundamental aspects of the Score Comparison Tool is changing (e.g. no tables or plots are changing).

In order to produce the Score Comparison Tool file, edit these variables and then run the file by clicking the 'play' button arrow in the top right of Visual Studio Code (if using another program google how to make a code run in that program if you don't know how). 

When running this pipeline, you may get some user warnings such as:  `UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.` This will not affect how well the program runs and you can ignore it.

# Making Future Changes to the Process
## SQL Queries
 The SQL details are kept in the utils folder in the `queries.py` file, if you want to edit or add more SQL queries, please add them here.

## Connection to the Database
Any time you want to connect to the database again, use the `connection` function that is kept in the utils folder in the `connection.py` file.  

## Requirements.txt
The `requirements.txt` file includes the packages and their versions that are used in this process, you need these installed in order to be able to run this process. To install new packages use `pip install package_name` in the command prompt/terminal.

## Potential Improvements to this RAP process
- Making the `scorecomparison.py` file into a single function so that the entire publication is done by running one python file, including other aspects (e.g. DQ Tables, PowerBi etc.)
- Improve the SQL queries 
    - shortening the Case Whens into a python function
- Is there a way to do unit tests?
