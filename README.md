# JEE Paper Checker
> Update: From 2023 onwards, automatic login does not work. See steps on How To Use to save response sheet and answer key manually .

Checking JEE mains response sheet manually is a disaster. This tool automatically check your response sheet with given answer key and shows you your marks. Also creates a review.html file showing correct, incorrect and unattempted questions

## Prerequisites
1) Python must be installed and on PATH
2) run `pip install -r requirements.txt` from working directory or install manually from pip all the requirements in file requirements.txt


## How to use
1) Open your response sheet -> Right click -> Save as (save in project working directory as `question_paper.html`)
2) Open answer key -> Right click -> Save as (save in project working directory as `answer_key.html`)
3) run `python check.py` 
4) Check out your marks in output. Also see review.html after this.
