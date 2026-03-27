from flask import Flask, render_template, request, session, redirect, url_for, Response
import database_manager as dbHandler
import hashlib
from salt import newSalt
import os
from dotenv import load_dotenv
from datetime import date, datetime
from math import ceil
from time import time
import contrast
import random

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

readMore = [
    "Brie-lieve Me",
    "Grate Read",
    "Curd Your Mind",
    "Say Cheese!",
    "Cheese the Day",
    "Gouda Read",
    "Feta-lous Read",
    "More Fondue?",
    "Mozza More",
    "Cheddar Up!",
    "Parm-tastic",
    "Blue Your Mind",
    "Fromage Fun",
    "Book & Brie",
    "Muenster Mind",
    "Halloumi Time",
    "Ricotta Read",
    "CamemRead",
    "Cheese Please",
    "Brie Curious?",
    "Feta Facts",
    "Explore Cheese",
    "Read Curd",
    "More Fromage",
    "Cheese the Book",
    "Learn Cheese",
    "Grate Ideas",
    "Say Brie More",
    "Curdious?",
    "Cheese & Read"
]

@app.route('/', methods=['GET', 'POST'])
def index():
    sort = request.args.get("sort")
    reverse = request.args.get('reverse')
    rateFilter = request.args.get("rateFilter")
    page = request.args.get('p')
    if page == None:
        page = 1
    try:
        page = int(page)
        if page < 1:
            raise Exception
    except:
        return redirect("/")

    return render_template('/index.html', page=page, session=session, sort=sort, reverse=reverse, rateFilter=rateFilter)


@app.route("/list-of-cheese", methods=['GET'])
def listOfCheese():
    page = int(request.args.get('p'))
    width = int(request.args.get("width"))
    height = int(request.args.get("height"))-45-(480/2)
    itemsPerPage = max(((width + 16) // 288)*(ceil(max(height/390.33, 1)))-1, 3 if height > width else 1)
    rateFilter = request.args.get("rateFilter") in ["true", "rateFilter"]
    amountOfPages = ceil((dbHandler.amountOfCheese()[0] - (0 if not rateFilter else dbHandler.amountOfRatings(session["userID"])))/itemsPerPage)

    sort = request.args.get("sort")
    if sort != "None":
        sort = [int(s) for s in sort.split("|")]
    else:
        sort = [0, 0]
    if request.args.get('reverse') in ["true", "reverse"]:
        sort[1] = 1 - sort[1]
    sortList = ["cheeseID", "cumulative_rating/amount_of_ratings", "rating"]
    direction = [" ASC", " DESC"]

    if page > amountOfPages:
        return redirect(f"list-of-cheese?p={int(amountOfPages)}&width={width}&height={request.args.get("height")}&rateFilter={request.args.get("rateFilter")}&sort={request.args.get("sort")}&reverse={request.args.get('reverse')}")

    madeSuggestion = None
    if session != {}:
        madeSuggestion = dbHandler.madeSuggestion(session["userID"])
        if madeSuggestion[0] == str(date.today()):
            madeSuggestion = True

    data = dbHandler.listCheese(page, itemsPerPage, sortList[sort[0]]+direction[sort[1]], rateFilter, None if session == {} else session["userID"])

    rated = None
    if session != {}:
        rated = dbHandler.rated(session["userID"])

    return render_template('/partials/cheeseList.html', content=data, session=session, amountOfPages=amountOfPages, width=width, page=page, rated=rated, madeSuggestion=madeSuggestion, readMore=random.sample(readMore, len(readMore)), sort=request.args.get('sort'), rateFilter=str(rateFilter).lower(), reverse=request.args.get('reverse'))


@app.route("/cheese", methods=['POST', 'GET'])
def cheese():
    cheeseID = request.args.get('cheeseID')
    if request.method == 'POST' and dbHandler.isRated(session["userID"], cheeseID) == []:
        rating = int(request.form["rating"])
        dbHandler.addRating(session["userID"], cheeseID, rating)
        return redirect(f"/cheese?cheeseID={cheeseID}")
    
    return render_template("/cheese.html", cheeseID=cheeseID)
    

@app.route("/cheese-content", methods=['GET'])
def cheeseContent():
    width = int(request.args.get("width"))
    height = int(request.args.get("height"))
    mobile = height > width
    cheeseID = request.args.get('cheeseID')
    data = dbHandler.specificCheese(cheeseID)
    rated = False
    rate = 0
    if session != {}:
        rateDB = dbHandler.isRated(session["userID"], cheeseID)
        rated = len(rateDB) != 0
        if rated != 0:
            rate = rateDB[0][3]
    return render_template("/partials/cheeseContent.html", content=data, session=session, rated=rated, rate=rate, cheeseID=cheeseID, mobile=mobile)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        if not dbHandler.userExists(username):
            return render_template("/login.html", failed=True)
        password = request.form['password'].strip()
        salt = dbHandler.getSalt(username)[0]
        password += salt
        password = hashlib.sha512(password.encode()).hexdigest()
        user = dbHandler.login(username, password)
        if user:
            session["userID"] = user[0][0]
            session["username"] = user[0][1]
            session["isDev"] = user[0][4]
            session["seen messages"] = 0
            session["colour"] = user[0][6]
            session["chatTimeout"] = user[0][7]
            session["newMessage"] = None
            return redirect(url_for("index"))
        else:
            return render_template("/login.html", failed=True)
    else:
        return render_template("/login.html")


@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        if dbHandler.userExists(username):
            return render_template("/register.html", failed=True)
        password = request.form['password'].strip()
        salt = newSalt()
        password += salt
        password = hashlib.sha512(password.encode()).hexdigest()
        dbHandler.register(username, salt, password)
        user = dbHandler.login(username, password)
        session["userID"] = user[0][0]
        session["username"] = user[0][1]
        session["isDev"] = user[0][4]
        session["seen messages"] = 0
        session["colour"] = user[0][6]
        session["chatTimeout"] = user[0][7]
        session["newMessage"] = None
        return redirect(url_for("index"))
    else:
        return render_template("/register.html")


@app.route("/suggest", methods=['POST', 'GET'])
def suggest():
    if session == {}:
        return redirect("/")
    if request.method == 'POST':
        madeSuggestion = dbHandler.madeSuggestion(session["userID"])
        if madeSuggestion[0] == str(date.today()):
            redirect(url_for("index"))
        if "image-submit" in request.form:
            name = request.form["cheese-name"]
            description = request.form["description"]
            img = request.form["img_url"]
            origin = request.form["origin"]
            return render_template("/suggest.html", session=session, img_url=img, name=name, description=description, origin=origin)
        elif "submit" in request.form:
            name = request.form["cheese-name"]
            description = request.form["description"]
            img = request.form["img_url"]
            origin = request.form["origin"]
            day = str(date.today())
            if session["isDev"] == "True":
                dbHandler.addCheese(name, description, img, origin)
            else:
                dbHandler.addSuggestion(name, description, img, origin, day, session["userID"])
            return redirect(url_for("index"))
    else:
        madeSuggestion = dbHandler.madeSuggestion(session["userID"])
        if madeSuggestion[0] == str(date.today()):
            return redirect(url_for("index"))
        return render_template("/suggest.html", session=session)


@app.route('/dev', methods=['GET'])
def dev():
    if session == {}:
        return redirect("/")
    if session["isDev"] != "True":
        return redirect(url_for("index"))
    data = dbHandler.listSuggestion()
    return render_template('/dev.html', content=data, session=session)


@app.route("/dev2", methods=['POST', 'GET'])
def dev2():
    if session == {}:
        return redirect("/")
    if session["isDev"] != "True":
        return redirect(url_for("index"))
    suggestionID = request.args.get('suggestionID')
    data = dbHandler.specificSuggestion(suggestionID)
    if request.method == 'POST':
        if "image-submit" in request.form:
            name = request.form["cheese-name"]
            description = request.form["description"]
            img = request.form["img_url"]
            origin = request.form["origin"]
            return render_template("/dev2.html", session=session, img_url=img, name=name, description=description, origin=origin)
        else:
            if "add" in request.form:
                name = request.form["cheese-name"]
                description = request.form["description"]
                img = request.form["img_url"]
                origin = request.form["origin"]
                dbHandler.addCheese(name, description, img, origin)
            dbHandler.removeSuggestion(suggestionID)
            return redirect(url_for("dev"))
    else:
        return render_template("/dev2.html", content=data, session=session, suggestionID=suggestionID)


@app.route("/the-cheese-files", methods=['GET'])
def files():
    return render_template("/the-cheese-files.html")


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('q')
    if query == "":
        query = None
    results = dbHandler.search(query)
    if query == "The Files":
        results = "the files"
    return render_template("/partials/search.html", results=results)


@app.route("/messages", methods=['GET'])
def chat_display():
    dateAndTimes = []
    usernameAndColours = []
    messages = dbHandler.getMessages()
    amount = dbHandler.amountOfMessages()
    newMessage = request.args.get("newMessage") == "True" and session["seen messages"][0] < amount[0] or session["newMessage"]
    session["newMessage"] = None
    if session["seen messages"] != amount:
        for i in range(len(messages)):
            user = dbHandler.getUser(messages[i][1])
            textColour = contrast.textColour(user[1])
            usernameAndColours.append([user[0], user[1], textColour])
            dateAndTimes.append([datetime.fromtimestamp(messages[i][3]).strftime("%I:%M %p").lstrip("0").lower(), datetime.fromtimestamp(messages[i][3]).strftime("%d/%m/%Y")])
        session["seen messages"] = amount
        return render_template("/partials/messages.html", messages=messages, session=session, dateAndTimes=dateAndTimes, usernameAndColours=usernameAndColours, newMessage = newMessage)
    return Response(status=204)


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if session == {}:
        return redirect("/")
    session["seen messages"] = None
    session["chatTimeout"] = dbHandler.getTimeout(session["userID"])[0][0]
    if request.method == "POST":
        if "delete" in request.form and session["isDev"] == "True":
            messageID = request.form["delete"]
            dbHandler.deleteMessage(messageID)
            return redirect(url_for("chat"))
        elif "delete" in request.form:
            messageID = request.form["delete"]
            dbHandler.softDeleteMessage(messageID)
            return redirect(url_for("chat"))
        if session["chatTimeout"] > float(time()):
            return redirect(url_for("chat"))
        message = request.form["message"].strip()
        if message != "" and len(message) <= 2000:
            if message.startswith("/timeout ") and session["isDev"] == "True":
                message = message.removeprefix("/timeout ")
                if not " " in message:
                    return Response(status=204)
                length, user = message.split(" ", 1)
                if not dbHandler.userExists(user):
                    return Response(status=204)
                seconds = float(time())
                for part in length.split("|"):
                    if part.endswith("d"):
                        seconds += int(part[:-1])*24*60*60
                    elif part.endswith("h"):
                        seconds += int(part[:-1])*60*60
                    elif part.endswith("m"):
                        seconds += int(part[:-1])*60
                    elif part.endswith("s"):
                        seconds += int(part[:-1])
                dbHandler.timeout(user, seconds)
                return redirect(url_for("chat"))
            if "eggman" in session["username"].lower() or "robotnik" in session["username"].lower():
                message = "I've come to make an announcement: Shadow the Hedgehog's a bitch-ass motherfucker, he pissed on my fucking wife. That's right, he took his hedgehog-fuckin' quilly dick out and he pissed on my fucking wife, and he said his dick was \"THIS BIG,\" and I said \"that's disgusting,\" so I'm making a callout post on my Twitter.com: Shadow the Hedgehog, you've got a small dick. It's the size of this walnut except WAY smaller. And guess what? Here's what my dong looks like. [Explosion sounds] That's right, baby. All points, no quills, no pillows — look at that, it looks like two balls and a bong! He fucked my wife, so guess what, I'm gonna fuck the Earth. That's right, this is what you get: MY SUPER LASER PISS!! Except I'm not gonna piss on the Earth, I'm gonna go higher; I'M PISSING ON THE MOON! How do you like that, Obama?! I PISSED ON THE MOON, YOU IDIOT! You have twenty-three hours before the piss DRRROPLLLETS hit the fucking Earth, now get outta my fucking sight, before I piss on you too!"
            dbHandler.addMessage(session["userID"], message, time())
            session["newMessage"] = True
            return redirect(url_for("chat"))
    elif request.method == "GET":
        session["seen messages"] = 0
        if session == {}:
            return redirect(url_for("index"))
        return render_template("/chat.html", session=session)
    return Response(status=204)


@app.route("/chat-input", methods=['GET'])
def chatInput():
    userID = request.args.get('userID')
    session["chatTimeout"] = dbHandler.getTimeout(userID)[0][0]
    length = [
        int((session["chatTimeout"]-float(time()))//86400),
        int(((session["chatTimeout"]-float(time()))%86400)//3600),
        int(((session["chatTimeout"]-float(time()))%3600)//60),
        int((session["chatTimeout"]-float(time()))%60)
    ]
    return render_template("/partials/chatInput.html", timeoutEnd=datetime.fromtimestamp(session["chatTimeout"]).strftime("%I:%M:%S %p %d/%m/%Y").lstrip("0").lower(), length=length, chatTimeout=session["chatTimeout"]>float(time())+1)



@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if session == {}:
        return redirect(url_for("index"))
    if request.method == "POST":
        password = request.form["password"].strip()
        salt = dbHandler.getSalt(session["username"])[0]
        password += salt
        password = hashlib.sha512(password.encode()).hexdigest()
        if not dbHandler.login(session["username"], password):
            return render_template("/profile.html", failedpass=True, session=session)
        if "delete" in request.form:
            dbHandler.deleteAccount(session["userID"])
            session.clear()
            return redirect(url_for("index"))
        username = request.form["username"].strip()
        if username != session["username"]:
            if dbHandler.userExists(username):
                return render_template("/profile.html", failed=True, session=session)
            dbHandler.updateUsername(session["userID"], username)
            session["username"] = username
        newPassword = request.form["new password"].strip()
        if newPassword != "":
            salt = dbHandler.getSalt(session["username"])[0]
            newPassword += salt
            newPassword = hashlib.sha512(newPassword.encode()).hexdigest()
            dbHandler.updatePassword(session["userID"], newPassword)
        colour = request.form["colour"]
        session["colour"] = colour
        dbHandler.updateColour(session["userID"], colour)
        return render_template("/profile.html", session=session, success=True)
            
    return render_template("/profile.html", session=session)


@app.route("/logout", methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for("index"))
    else:
        return render_template("/logout.html", session=session)


@app.route("/ai", methods=['POST'])
def ai():
    query = request.form["query"]
    return redirect(f"https://www.google.com/search?q={query}")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
