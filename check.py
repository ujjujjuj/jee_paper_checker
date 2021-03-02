from bs4 import BeautifulSoup as soup
import re

subjects = ["po","ps","co","cs","mo","ms"]

def getQuestions(quespaper):
    marked = []
    quesGroups = quespaper.findAll("div",{"class":"section-cntnr"})
    for i in range(len(quesGroups)):
        quesDivs = quesGroups[i].findAll("div",{"class":"question-pnl"})
        for quesDiv in quesDivs:
            qType = quesDiv.find("td",text=re.compile("Question Type")).findNext('td').contents[0]
            status = quesDiv.find("td",text=re.compile("Status")).findNext('td').contents[0]
            if status in ["Not Answered","Not Attempted and Marked For Review"]:
                continue
            qID = quesDiv.find("td",text=re.compile("Question ID")).findNext('td').contents[0]
            if qType == "MCQ":
                ansNumber = quesDiv.find("td",text=re.compile("Chosen Option")).findNext('td').contents[0]
                ans = quesDiv.find("td",text=re.compile(f"Option {ansNumber} ID")).findNext('td').contents[0]
            elif qType == "SA":
                ans = quesDiv.find("td",text=re.compile("Given Answer")).findNext('td').contents[0]
                if ans.strip() == "--":
                    continue
            marked += [[qID,ans,qType,subjects[i]]]
    return marked

def getAnswers(anskey):
    key = {}
    ansRows = anskey.find("table",{"class":"table table-bordered table-condensed"}).findAll(class_=None,recursive=False)
    for ansRow in ansRows:
        qID = ansRow.find("span",id=re.compile("QuestionNo")).contents[0]
        ans = ansRow.find("span",id=re.compile("RAnswer")).contents[0]
        key[str(qID)]=ans
    return key

def checkPaper(marked,key):
    marks = 0
    correct = []
    incorrect = []
    subjectWise = [0,0,0,0,0,0]
    for ques in marked:
        if ques[1] == key[ques[0]]:
            marks += 4
            correct += [ques[0]]
            subjectWise[subjects.index(ques[3])] += 4
        else:
            incorrect += [ques[0]]
            if ques[2]=="MCQ":
                marks -=1
                subjectWise[subjects.index(ques[3])] -= 1
    return marks,correct,incorrect, subjectWise

qpaperHTML = ""
anskeyHTML = ""
with open("question_paper.html","r") as f:
    qpaperHTML = f.read()
with open("answer_key.html","r") as f:
    anskeyHTML = f.read()

quespaper = soup(qpaperHTML,"lxml")
anskey = soup(anskeyHTML,"lxml")

marked = getQuestions(quespaper)
key = getAnswers(anskey)
marks,correct,incorrect,subjectWise = checkPaper(marked,key)

print(f"You have scored {marks} marks out of 300")
print(f"You attempted {len(correct)} correct questions and {len(incorrect)} incorrect questions.")
print(f"Physics: {subjectWise[0]} + {subjectWise[1]}")
print(f"Chemistry: {subjectWise[2]} + {subjectWise[3]}")
print(f"Maths: {subjectWise[4]} + {subjectWise[5]}\n")
print(f"Correct questions: {correct}\n")
print(f"Incorrect questions: {incorrect}")

