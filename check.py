from bs4 import BeautifulSoup as soup
import re
import json

subjects = ["physics", "chemistry", "math"]


class Question:
    def __init__(self, qType, subject, qID, ans, quesUrl, ansUrls, chosenOptionNumber, optionIds):
        self.qType = qType
        self.qID = qID
        self.subject = subject
        self.status = "unattempted"
        self.ans = ans
        self.correctAns = ans
        self.quesUrl = quesUrl
        self.ansUrls = ansUrls
        try:
            self.chosenOptionNumber = int(chosenOptionNumber)
        except:
            self.chosenOptionNumber = 0
        self.correctAnsNumber = "None"
        self.optionIds = optionIds

    def __repr__(self):
        return f'Question({self.subject} {self.qType})'


def getMarked(quespaper):
    marked = []
    questions = quespaper.findAll("td", {"class": "rw"})
    qno = 1
    for question in questions:
        images = question.findAll("img")
        quesUrl = images[0]['src']
        ansUrls = [img['src'] for img in images[1:]]
        qType = question.find("td", text=re.compile(
            "Question Type")).findNext('td').contents[0]
        status = question.find("td", text=re.compile(
            "Status")).findNext('td').contents[0]
        qID = question.find("td", text=re.compile(
            "Question ID")).findNext('td').contents[0]
        subject = subjects[(qno-1)//30]
        optionIds = []
        ansNumber = -1
        if status in ["Not Answered", "Not Attempted and Marked For Review"]:
            ans = "NA"
            if qType == "MCQ":
                for i in range(4):
                    optionIds.append(question.find("td", text=re.compile(
                        f"Option {i+1} ID")).findNext('td').contents[0])
        elif qType == "MCQ":
            for i in range(4):
                optionIds.append(question.find("td", text=re.compile(
                    f"Option {i+1} ID")).findNext('td').contents[0])
            ansNumber = question.find("td", text=re.compile(
                "Chosen Option")).findNext('td').contents[0]
            ans = question.find("td", text=re.compile(
                f"Option {ansNumber} ID")).findNext('td').contents[0]
        elif qType == "SA":
            ans = question.find("td", text=re.compile(
                "Given Answer")).findNext('td').contents[0]
            ansNumber = ans
            if ans.strip() == "--":
                ans = "NA"
        qno += 1
        marked.append(Question(qType, subject, qID, ans,
                      quesUrl, ansUrls, ansNumber, optionIds))

    return marked


def getAnswers(anskey):
    key = {}
    # ansRows = anskey.find("table",{"class":"table table-bordered table-condensed"}).findAll("tbody")[0]
    qids = anskey.findAll("span", id=re.compile("QuestionNo"))
    answers = anskey.findAll("span", id=re.compile("RAnswer"))
    for qid, ans in zip(qids, answers):
        key[qid.text] = ans.text

    return key


def checkPaper(marked, key):
    marks = 0
    correct = []
    incorrect = []
    unattempted = []
    subjectWise = [0, 0, 0, 0, 0, 0]
    for ques in marked:
        ques.correctAns = key[ques.qID]
        if ques.qType == "MCQ":
            ques.correctAns = ques.optionIds.index(key[ques.qID]) + 1
        if ques.ans == "NA":
            unattempted.append(ques)
            ques.correctAns = key[ques.qID]
        elif ques.ans == key[ques.qID]:
            marks += 4
            correct.append(ques)
            ques.status = "correct"
            qCategory = subjects.index(
                ques.subject)*2 + (1 if ques.qType == "SA" else 0)
            subjectWise[qCategory] += 4
        else:
            if ques.qType == "MCQ":
                ques.correctAns = ques.optionIds.index(key[ques.qID]) + 1
            incorrect.append(ques)

            marks -= 1
            ques.status = "incorrect"
            qCategory = subjects.index(
                ques.subject)*2 + (1 if ques.qType == "SA" else 0)
            subjectWise[qCategory] -= 1

    return marks, [correct, incorrect, unattempted], subjectWise


def makeJSON(data):
    finalJson = {"correct": [], "incorrect": [], "unattempted": []}
    j = 0
    for i in finalJson:
        for ques in data[j]:
            finalJson[i].append([ques.quesUrl, ques.ansUrls, ques.chosenOptionNumber,
                                ques.correctAns if ques.correctAnsNumber == "None" else ques.correctAnsNumber])
        j += 1
    return finalJson


qpaperHTML = ""
anskeyHTML = ""
with open("question_paper.html", "r") as f:
    qpaperHTML = f.read()
with open("answer_key.html", "r") as f:
    anskeyHTML = f.read()

quespaper = soup(qpaperHTML, "lxml")
anskey = soup(anskeyHTML, "lxml")

marked = getMarked(quespaper)

key = getAnswers(anskey)
marks, data, subjectWise = checkPaper(marked, key)
jsonData = json.dumps(makeJSON(data))
html = """\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Review</title>
    <link rel="stylesheet"href="http://fonts.googleapis.com/css?family=Noto Sans JP"/>
    <style>
    * {
      padding: 0;
      margin: 0;
      outline: none;
      box-sizing: border-box;
      font-family: Noto Sans JP;
    }
    body {
      background: #eee;
    }
    nav {
      display: flex;
      padding: 2vh 2vw;
    }
    .btn {
      border: none;
      font-size: 1.6vh;
      color: var(--c);
      padding: 1.2vh 2vw;
      margin: 0 2vw;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.3s;
      border: 2px solid var(--c);
    }
    .btn:hover {
      background: var(--c);
      color: #eee;
    }
    .btn:active {
      transform: scale(0.9);
    }
    .active {
      box-shadow: 0 0 10px var(--c);
      background: var(--c);
      color: #eee;
    }

    .corrects,
    .wrongs,
    .uns {
      display: flex;
      flex-wrap: wrap;
      padding: 2vh 2vw;
    }
    .corrects {
      background: #32936f;
    }
    .wrongs {
      background: #e83f6f;
    }
    .uns {
      background: #c3960c;
    }
    .item {
      display: flex;
      flex-direction: column;
      width: 100%;
      border-radius: 10px;
      background: #fff;
      box-shadow: 0 0 10px #1e1e2434;
      padding: 2vh 2vw;
      margin-bottom: 4vh;
    }
    .item h3 {
      margin-bottom: 1vh;
    }
    .q {
      width: 50%;
      margin-bottom: 2vh;
    }
    .opts {
      width: 60%;
      padding: 3vh 0;
      padding-left: 2vw;
      position: relative;
      border-top: 2px #5f0a87 solid;
      border-bottom: 2px #5f0a87 solid;
      background: #fff;
      margin-bottom: 3vh;
    }
    .opts::before {
      position: absolute;
      top: 1vh;
      left: 5px;
      content: "Options: ";
    }
    .opt {
      transform: translateY(10px);
    }
    .item h2 {
      font-size: 2vh;
      margin-bottom: 1vh;
    }
    </style>
  </head>
  <body>
    <nav>
      <h1>Sort By:</h1>
      <div style="--c: #32936f" id="correct" class="btn">Correct</div>
      <div style="--c: #e83f6f" id="incorrect" class="btn">Incorrect</div>
      <div style="--c: #c3960c" id="un" class="btn">Unattempted</div>
      <div style="--c: #2274a5" id="all" class="btn active">All</div>
    </nav>

    <div class="root">
      <div class="corrects"></div>
      <div class="wrongs"></div>
      <div class="uns"></div>
    </div>

    <script>
      const json = """+jsonData+"""
      // Correct
      let corrects = document.querySelector(".corrects");
      for (let correct of json.correct) {
        let q = document.createElement("DIV");
        q.classList.add("item");
        for (let elem of correct) {
          if (parseInt(elem)) {
            let h2 = document.createElement("H2");
            h2.textContent = elem;
            q.appendChild(h2);
          } else if (Array.isArray(elem)) {
            let opts = document.createElement("OL");
            opts.classList.add("opts");
            for (let opt of elem) {
              let li = document.createElement("LI");
              let img = document.createElement("IMG");
              img.classList.add("opt");
              img.setAttribute("src", opt);
              li.appendChild(img);
              opts.appendChild(li);
            }
            q.appendChild(opts);
          } else {
            let img = document.createElement("IMG");
            img.classList.add("q");
            img.setAttribute("src", elem);
            q.appendChild(img);
          }
        }
        corrects.appendChild(q);
      }

      // Wrong
      let wrongs = document.querySelector(".wrongs");
      for (let correct of json.incorrect) {
        let q = document.createElement("DIV");
        q.classList.add("item");
        for (let elem of correct) {
          if (parseInt(elem)) {
            let h2 = document.createElement("H2");
            h2.textContent = elem;
            q.appendChild(h2);
          } else if (Array.isArray(elem)) {
            let opts = document.createElement("OL");
            opts.classList.add("opts");
            for (let opt of elem) {
              let li = document.createElement("LI");
              let img = document.createElement("IMG");
              img.classList.add("opt");
              img.setAttribute("src", opt);
              li.appendChild(img);
              opts.appendChild(li);
            }
            q.appendChild(opts);
          } else {
            let img = document.createElement("IMG");
            img.classList.add("q");
            img.setAttribute("src", elem);
            q.appendChild(img);
          }
        }
        wrongs.appendChild(q);
      }

      // Uns
      let uns = document.querySelector(".uns");
      for (let correct of json.unattempted) {
        let q = document.createElement("DIV");
        q.classList.add("item");
        for (let elem of correct) {
          if (parseInt(elem)) {
            let h2 = document.createElement("H2");
            h2.textContent = elem;
            q.appendChild(h2);
          } else if (Array.isArray(elem)) {
            let opts = document.createElement("OL");
            opts.classList.add("opts");
            for (let opt of elem) {
              let li = document.createElement("LI");
              let img = document.createElement("IMG");
              img.classList.add("opt");
              img.setAttribute("src", opt);
              li.appendChild(img);
              opts.appendChild(li);
            }
            q.appendChild(opts);
          } else {
            let img = document.createElement("IMG");
            img.classList.add("q");
            img.setAttribute("src", elem);
            q.appendChild(img);
          }
        }
        uns.appendChild(q);
      }

      let qs = document.querySelectorAll(".q");
      let index = 1;
      for (let q of qs) {
        let h3 = document.createElement("H3");
        h3.textContent = `Question ${index}: `;
        q.parentElement.insertBefore(h3, q);

        index++;
      }

      let items = document.querySelectorAll(".item");
      for (let item of items) {
        if (!item.parentElement.classList.contains("uns")) {
          let oldTxt = item.childNodes[3].textContent;
          item.childNodes[3].textContent = `Chosen Option: ${oldTxt}`;

          let oldTxt2 = item.childNodes[4].textContent;
          item.childNodes[4].textContent = `Answer: ${oldTxt2}`;
        } else {
          item.childNodes[3].textContent = `Not attempted`;
          let oldTxt2 = item.childNodes[4].textContent;
          item.childNodes[4].textContent = `Answer: ${oldTxt2}`;
        }
      }

      // BTNS
      let btns = document.querySelectorAll(".btn");

      for (let btn of btns) {
        btn.addEventListener("click", () => {
          if (document.querySelector(".active")) {
            document.querySelector(".active").classList.remove("active");
          }
          document.querySelector(".corrects").style.display = "none";
          document.querySelector(".wrongs").style.display = "none";
          document.querySelector(".uns").style.display = "none";

          btn.classList.add("active");
          if (btn.getAttribute("id") == "correct") {
            document.querySelector(".corrects").style.display = "flex";
          } else if (btn.getAttribute("id") == "incorrect") {
            document.querySelector(".wrongs").style.display = "flex";
          } else if (btn.getAttribute("id") == "un") {
            document.querySelector(".uns").style.display = "flex";
          } else {
            document.querySelector(".corrects").style.display = "flex";
            document.querySelector(".wrongs").style.display = "flex";
            document.querySelector(".uns").style.display = "flex";
          }
        });
      }

      let noOfC = `Correct (${corrects.children.length})`;
      let noOfI = `Incorrect (${wrongs.children.length})`;
      let noOfU = `Unattempted (${uns.children.length})`;

      document.querySelector("#correct").textContent = noOfC;
      document.querySelector("#incorrect").textContent = noOfI;
      document.querySelector("#un").textContent = noOfU;
    </script>
  </body>
</html>

"""
with open("review.html", "w") as f:
    f.write(html)

print(f"You have scored {marks} marks out of 300")
print(
    f"You attempted {len(data[0])} correct questions and {len(data[1])} incorrect questions.")
print(f"Physics: {subjectWise[0]} + {subjectWise[1]}")
print(f"Chemistry: {subjectWise[2]} + {subjectWise[3]}")
print(f"Maths: {subjectWise[4]} + {subjectWise[5]}\n")
print("Other information is provided in review.html")
