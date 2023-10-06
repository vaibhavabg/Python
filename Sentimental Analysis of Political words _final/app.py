from flask import Flask, request, render_template,session,redirect,url_for
import numpy as np
import matplotlib
import cv2
import dlib
import time
from datetime import datetime
import os


#import db
import sqlite3 as sql
import pickle



from flask import Flask, request, render_template
from sklearn.feature_extraction.text import TfidfVectorizer


from sklearn.metrics.pairwise import cosine_similarity
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


import pandas as pd



import nltk

#!from nltk.corpus import punkt
from string import punctuation
import re
from nltk.corpus import stopwords

app = Flask(__name__)


app.config['SECRET_KEY'] = 'super secret key'


@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("aboutus.html")



@app.route("/signup", methods = ["GET","POST"])
def signup():
    msg=None
    if(request.method=="POST"):
        if (request.form["uname"]!="" and request.form["uphone"]!="" and request.form["username"]!="" and request.form["upassword"]!=""):
            uname=request.form["uname"]
            uphone=request.form["uphone"]
            username=request.form["username"]
            password=request.form["upassword"]
          


            with sql.connect("textemotion.db") as con:
                c=con.cursor()
                c.execute("INSERT INTO  signup VALUES('"+uname+"','"+uphone+"','"+username+"','"+password+"')")
                msg = "Your account is created"

                con.commit()
        else:
            msg="Something went wrong"


    return render_template("signup.html", msg=msg)


@app.route('/userlogin')
def userlogin():
    return render_template("userlogin.html")

@app.route('/userloginNext',methods=['GET','POST'])
def userloginNext():
    msg=None
    if (request.method == "POST"):
        username = request.form['username']
      
        upassword = request.form['upassword']
        
        with sql.connect("textemotion.db") as con:
            c=con.cursor()
            c.execute("SELECT username,upassword  FROM signup WHERE username = '"+username+"' and upassword ='"+upassword+"'")
            r=c.fetchall()
            for i in r:
                if(username==i[0] and upassword==i[1]):
                    session["logedin"]=True
                    session["fusername"]=username
                    return redirect(url_for("userhome"))
                else:
                    msg= "please enter valid username and password"
    
    return render_template("userlogin.html",msg=msg)



@app.route('/adminlogin')
def adminlogin():
    return render_template("adminlogin.html")

@app.route('/adminloginNext',methods=['GET','POST'])
def adminloginNext():
    msg=None
    if (request.method == "POST"):
        ausername = request.form['ausername']
      
        apassword = request.form['apassword']
        
        with sql.connect("textemotion.db") as con:
            c=con.cursor()
            c.execute("SELECT ausername,apassword  FROM adminlogin WHERE ausername = '"+ausername+"' and apassword ='"+apassword+"'")
            r=c.fetchall()
            for i in r:
                if(ausername==i[0] and apassword==i[1]):
                    session["logedin"]=True
                    session["fusername"]=ausername
                    return redirect(url_for("adminhome"))
                else:
                    msg= "please enter valid username and password"
    
    return render_template("adminlogin.html",msg=msg)




#usercode
@app.route('/userhome')
def userhome():
    return render_template("userhome.html")



@app.route('/usergallery')
def usergallery():
    return render_template("usergallery.html")







@app.route("/addfaq", methods = ["GET","POST"])
def addfaq():
    msg=None
    if(request.method=="POST"):
        if (request.form["question"]!="" and request.form["answer"]!=""):
            question=request.form["question"]
            answer=request.form["answer"]
        
           


            with sql.connect("textemotion.db") as con:
                c=con.cursor()
                c.execute("INSERT INTO  faq VALUES('"+question+"','"+answer+"')")
                msg = "Your Query saved successfully "

                con.commit()
        else:
            msg="Something went wrong"


    return render_template("adminaddfaq.html", msg=msg)


@app.route('/userlogout')
def userlogout():
	# Remove the session variable if present
	session.clear()
	return redirect(url_for('index'))

#admin base
@app.route('/adminhome')
def adminhome():
    return render_template("adminhome.html")

@app.route('/viewusers')
def viewusers():
    con=sql.connect("textemotion.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select uname,uphone,username from signup")
    rows=cur.fetchall()
    print(rows)
    return render_template("adminviewusers.html",rows=rows)


@app.route('/viewqueries')
def viewqueries():
    con=sql.connect("textemotion.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select question,answer from faq")
    rows=cur.fetchall()
    print(rows)
    return render_template("userviewfaq.html",rows=rows)

@app.route('/adminviewqueries')
def adminviewqueries():
    con=sql.connect("textemotion.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select question,answer from faq")
    rows=cur.fetchall()
    print(rows)
    return render_template("adminviewfaq.html",rows=rows)

@app.route('/adminlogout')
def adminlogout():
	# Remove the session variable if present
	session.clear()
	return redirect(url_for('index'))




nltk.download('stopwords')

set(stopwords.words('english'))



@app.route('/my_form')
def my_form():
    return render_template('predict.html')

@app.route('/home', methods=['POST'])
def my_form_post():
    stop_words = stopwords.words('english')
    
    #!convert to lowercase
    text1 = request.form['text1'].lower()
    
    text_final = ''.join(c for c in text1 if not c.isdigit())
    
    #*remove punctuations
    #^text3 = ''.join(c for c in text2 if c not in punctuation)
        
    #?remove stopwords    
    processed_doc1 = ' '.join([word for word in text_final.split() if word not in stop_words])

    sanalyzer = SentimentIntensityAnalyzer()
    dd = sanalyzer.polarity_scores(text=processed_doc1)
    dd['text'] = processed_doc1

    #*create a dataframe
    df = pd.DataFrame(dd, index=[0])

    #!create a vectorizer
    vectorizer = TfidfVectorizer()

    #*create a matrix
    matrix = vectorizer.fit_transform(df['text'])
    #&create a similarity matrix

    sim_matrix = cosine_similarity(matrix)
    #?create a similarity matrix
    
    sim_matrix = sim_matrix.flatten()
    

    compound = round((1 + dd['compound'])/2, 2)

    return render_template('predict.html', final=compound, text1=text_final,text2=dd['pos'],text5=dd['neg'],text4=compound,text3=dd['neu'], text6=sim_matrix)




if __name__ == "__main__":
    app.run(debug=True)
