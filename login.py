from config import *
import requests
from PIL import Image

sess = requests.Session()
res = sess.get("https://testservices.nic.in/examsys21/root/AuthForAdmitCardDwd.aspx?enc=Ei4cajBkK1gZSfgr53ImFVj34FesvYg1WX45sPjGXBoodsCAPgItCPvwv6bGBGio").content.decode()
viewstate = res.split('id="__VIEWSTATE" value="')[1].split('" />')[0]
viewstategen = res.split('id="__VIEWSTATEGENERATOR" value="')[1].split('" />')[0]
eventvalidation = res.split('id="__EVENTVALIDATION" value="')[1].split('" />')[0]
captcha_img = sess.get("https://testservices.nic.in/examsys21/Handler/captchahandler.ashx", stream=True).raw
im = Image.open(captcha_img)
im.show()
captcha = input("Enter captcha: ")
reqbody = {
    "__VIEWSTATE":viewstate,
    "__VIEWSTATEGENERATOR":viewstategen,
    "__EVENTVALIDATION":eventvalidation,
    "ctl00$ContentPlaceHolder1$txtRegno": APPLICATION_NUMBER,
    "ctl00$ContentPlaceHolder1$ddlday": DOB.split("-")[0],
    "ctl00$ContentPlaceHolder1$ddlmonth": DOB.split("-")[1],
    "ctl00$ContentPlaceHolder1$ddlyear": DOB.split("-")[2],
    "ctl00$ContentPlaceHolder1$txtsecpin": captcha,
    "ctl00$ContentPlaceHolder1$hdnpwd": "",
    "ctl00$ContentPlaceHolder1$btnsignin": "Sign In"
}
sess.post("https://testservices.nic.in/examsys21/root/AuthForAdmitCardDwd.aspx?appFormId=101032111",data=reqbody)

res = sess.get("https://testservices.nic.in/ExamSys21/Registration/Index.aspx").content.decode()
paperurl = res.split('id="ctl00_LoginContent_rptViewQuestionPaper_ctl01_lnkviewKey" class="btn btn-primary" href="')[1].split('" target="_blank"')[0]

with open("question_paper.html","w") as f:
    f.write(sess.get(paperurl).content.decode().replace("/per","https://cdn3.digialm.com//per"))
print("Saved question_paper.html")

with open("answer_key.html","w") as f:
    f.write(sess.get("https://testservices.nic.in/ExamSys21/KeyChallange/AnswerKey.aspx").content.decode().replace("../","/ExamSys21/").replace("/ExamSys21/","https://testservices.nic.in/ExamSys21/"))
print("Saved answer_key.html")