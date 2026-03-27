import sqlite3 as sql
database = "database/data_source.db"


def sqlCommand(command, var = ()):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute(command, var).fetchall()
    return data


def listCheese(page, itemsPerPage, sort, rated, userID):
    con = sql.connect(database)
    cur = con.cursor()
    data = cur.execute(f'SELECT cheese.*, ratings.rating FROM cheese LEFT JOIN ratings ON cheese.cheeseID = ratings.cheeseID AND ratings.userID = 1 {f"WHERE NOT EXISTS (SELECT cheeseID FROM ratings WHERE cheese.cheeseID = ratings.cheeseID AND userID = {userID})" if rated else ""} ORDER BY {sort} {"NULLS LAST" if "e" not in sort else ""} LIMIT ? OFFSET ?', (itemsPerPage, (page-1)*itemsPerPage,)).fetchall()
    con.close()
    return data


def amountOfCheese():
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT count(*) FROM cheese").fetchall()
    return data[0]


def specificCheese(cheeseID):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT * FROM cheese WHERE cheeseID = ? LIMIT 1", (cheeseID,)).fetchall()
    return data[0]


def login(username, password):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?) AND password = ? LIMIT 1", (username, password,)).fetchall()
    return data


def getSalt(username):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT salt FROM users WHERE LOWER(username) = LOWER(?) LIMIT 1", (username,)).fetchall()
    return data[0]


def userExists(username):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?) LIMIT 1", (username,)).fetchall()
    return data


def register(username, salt, password):
    with sql.connect(database) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, salt, password) VALUES (?, ?, ?)", (username, salt, password))


def isRated(userID, cheeseID):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT * FROM ratings WHERE userID = ? AND cheeseID = ?", (userID, cheeseID)).fetchall()
    return data


def addRating(userID, cheeseID, rating):
    with sql.connect(database) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO ratings (userID, cheeseID, rating) VALUES (?, ?, ?)", (userID, cheeseID, rating))
        cur.execute("UPDATE cheese SET amount_of_ratings = amount_of_ratings + 1, cumulative_rating = cumulative_rating + ? WHERE cheeseID = ?", (rating, cheeseID))


def madeSuggestion(userID):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT lastSuggestion FROM users WHERE userID = ? LIMIT 1", (userID,)).fetchall()
    return data[0]


def addSuggestion(name, description, img, origin, day, userID):
    with sql.connect(database) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO suggestions (name, description, image, place_of_origin) VALUES (?, ?, ?, ?)", (name, description, img, origin))
        cur.execute("UPDATE users SET lastSuggestion = ? WHERE userID = ?", (day, userID))


def listSuggestion():
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT * FROM suggestions").fetchall()
    return data


def specificSuggestion(suggestionID):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT * FROM suggestions WHERE suggestionID = ? LIMIT 1", (suggestionID,)).fetchall()
    return data[0]


def addCheese(name, description, img, origin):
    with sql.connect(database) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO cheese (name, cumulative_rating, description, image, place_of_origin, amount_of_ratings) VALUES (?, ?, ?, ?, ?, ?)", (name, 0, description, img, origin, 0))


def removeSuggestion(suggestionID):
    with sql.connect(database) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM suggestions WHERE suggestionID = ?", (suggestionID,))


def rated(userID):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT cheeseID FROM ratings WHERE userID = ?", (userID,)).fetchall()
    return data


def search(query):
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT * FROM cheese WHERE name LIKE ? OR description LIKE ? OR place_of_origin LIKE ? ORDER BY cumulative_rating/5/amount_of_ratings DESC NULLS LAST LIMIT 15", (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    return data


def getMessages():
    with sql.connect(database) as con:
        cur = con.cursor()
        data = cur.execute("SELECT * FROM chat ORDER BY time").fetchall()
    return data


def addMessage(userID, message, time):
    sqlCommand("INSERT INTO chat(userID, message, time) VALUES(?, ?, ?)", (userID, message, time))


def deleteMessage(messageID):
    sqlCommand("DELETE FROM chat WHERE messageID = ?", (messageID,))


def getUser(userID):
    return sqlCommand("SELECT username, colour FROM users WHERE userID = ?", (userID,))[0]


def updateUsername(userID, username):
    sqlCommand("UPDATE users SET username = ? WHERE userID =?", (username, userID))


def updatePassword(userID, password):
    sqlCommand("UPDATE users SET password = ? WHERE userID =?", (password, userID))


def updateColour(userID, colour):
    sqlCommand("UPDATE users SET colour = ? WHERE userID =?", (colour, userID))


def timeout(username, length):
    sqlCommand("UPDATE users SET chatTimeout = ? WHERE username = ?", (length, username))


def getTimeout(userID):
    return sqlCommand("SELECT chatTimeout FROM users WHERE userID = ?", (userID,))


def softDeleteMessage(messageID):
    sqlCommand("UPDATE chat SET deleted = 'True' WHERE messageID = ?", (messageID,))


def amountOfMessages():
    return (sqlCommand("SELECT count(*) FROM chat")[0][0], sqlCommand("SELECT count(*) FROM chat WHERE deleted IS NULL")[0][0])


def deleteAccount(userID):
    sqlCommand("DELETE FROM users WHERE userID = ?", (userID,))
    sqlCommand("DELETE FROM chat WHERE userID = ?", (userID,))
    sqlCommand("DELETE FROM ratings WHERE userID = ?", (userID,))


def amountOfRatings(userID):
    return sqlCommand("SELECT count(*) FROM ratings WHERE userID = ?", (userID,))[0][0]