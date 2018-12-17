import requests

"""
You don't need to know ahead of time how many games there are in your collection. This script will collect
your entire backloggery.com video game collection and export it to a .csv or .xlsx file. It collects the
following pieces of information for each game:

    1. Name of game
    2. Console
    3. Achievement numbers (if set)
    4. Game completion status
    5. Game comments
    6. Compilations: get the individual games in the compilation
    Here is the network path for getting all of the games in a compilation:

    https://backloggery.com/ajax_expandcomp.php?user=originalKILLJOY&comp_sys=XBO&comp=Minecraft:+Story+Mode+-+A+Telltale+Games+Series

TODO:
1. You can even download your friend's collections and make comparisons per console.
2. Idea: scrape Xbox game art images from xbox.com

"""

backloggery_username = "originalKILLJOY"
export_to_csv  = True
export_to_xlsx = True

count = 0
iterations = 1
backloggery_backup = []
gameDetails = []
gameDetailsMatrix = []
compGameDetails = []
currentConsole = ""
completionStatus = ""
name = ""
comments = ""
achievements = ""
compilationName = ""
system = ""


def getCompilationGames(compName, system):
    print("Entering getCompilationGames", compName)
    global compilationName
    compilationName = compName

    # Use the passed in compilation name to request the list of associated games
    compQueryName = compName.replace(" ", "+")
    compURL = "https://backloggery.com/ajax_expandcomp.php?user=" + backloggery_username \
    + "&comp_sys=" + system + "&comp=" + compQueryName
    c = requests.get(compURL)
    compilationGames = c.content.decode("utf-8")
    compilationGames = compilationGames.strip('\t\t').split('\n')
    print("compURL", compURL)

    # Parse the compilation games and add them to the overall gameDetails list
    x = 0
    while x < len(compilationGames):

        currentLine = compilationGames[x].strip()
        parseLogic(currentLine)
        x += 1

    appendGameList(currentLine)
    compilationName = ""

def getCompilationNames(currentLine):
    global system
    compilationName = currentLine.split('<')[0].strip()
    print("\nCompilation: ", compilationName)
    gameDetailsRow = currentConsole + "," + compilationName
    getCompilationGames(compilationName, system)


def getSystem(currentLine):
    global system
    system = currentLine.split('</b>')[0]
    #print("System is:", system)


def getComments(currentLine):
    global comments
    comments1 = ""
    comments2 = ""
    #comments = currentLine.split('>')[3].split('<')[0]
    splitLine = currentLine.split('getComments')
    part1 = splitLine[0]
    if "gamerow" in part1:
        comments1 = part1.split('"gamerow">')[1].split('<')[0] + "|"
    part2 = splitLine[1].replace('&#x25BC;', "").strip()
    comments2 = part2.split('>')[3].split('<')[0]
    comments = comments1 + comments2
    comments.replace(",", ";")

def getAchievements(currentLine):
    global achievements
    part1 = currentLine.split('<table class="achievebar">')[0]
    achievements = part1.split('<b>')[1].replace('</b>', "")
    #print(achievements)


def getName(currentLine):
    global name
    cutoff = len(currentLine) - 4
    name = currentLine[3:cutoff]
    #print("\nName is:", name)


def getStatus(currentLine):
    global completionStatus
    global name
    splitLine = currentLine
    completionStatus = splitLine.split('(')[1].split(')')[0]
    #print("\nStatus is:", completionStatus)

    # Case of name on the same line as the status. For example:
    # <a href="games.php?user=originalkilljoy&amp;console=360&amp;status=2"><img alt="(B)"
    # width="16" height="16" src="images/beaten.gif" /></a> <b>Assassin's Creed</b>
    if "status=2" in currentLine or "status=3" in currentLine:
        name = currentLine.split('<b>')[1].split('<')[0]

def getConsole(currentLine):
    global currentConsole
    if currentLine.startswith('</section>'):
        currentLine = currentLine[10:]
    currentLine = currentLine.split('>')
    currentConsole = currentLine[3].split('<')[0]
    #print("\n\nConsole is:", currentConsole)

def appendGameList(currentLine):
    #print("-------------------------------------------------")
    global completionStatus, name, comments, achievements, compilationName
    gameDetailsRow = currentConsole   + "," + \
                     completionStatus + "," + \
                     compilationName  + "," + \
                     name             + "," + \
                     achievements     + "," + \
                     comments

    gameDetailsRow2 = [currentConsole, completionStatus, compilationName, name, achievements, comments]
    if name:
        gameDetails.append(gameDetailsRow)
        gameDetailsMatrix.append(gameDetailsRow2)

    completionStatus = ""
    name = ""
    comments = ""
    achievements = ""
    system = ""

def parseLogic(currentLine):

    # Get system for compilations
    if '</b>' and '</div>' in currentLine and 'achievebar' not in currentLine:
        getSystem(currentLine)

    # Reached the beginning of a new game row
    if '<section class="gamebox">' in currentLine:
        appendGameList(currentLine)

    # Get console
    elif 'class="gamebox systemend"' in currentLine:
        getConsole(currentLine)

    # Get status
    elif 'alt="(' in currentLine:
        getStatus(currentLine)

    # Get name
    elif currentLine.startswith('<b>') and currentLine.endswith('</b>'):
        getName(currentLine)

    # Get achievements
    elif 'achievebar' in currentLine:
        getAchievements(currentLine)

    # Get comments
    elif 'getComments' in currentLine:
        getComments(currentLine)

    # Part of a compilation?
    elif 'getComp(' in currentLine:
        getCompilationNames(currentLine)



moreGames = True
while moreGames:

    targetURL = "https://backloggery.com/ajax_moregames.php?user=" + backloggery_username + "&ajid=" + str(count)
    #targetURL = "https://backloggery.com/ajax_moregames.php?user=originalKILLJOY&ajid=" + str(count)
    r = requests.get(targetURL)

    # Using r.content returns bytes, which works with decode and allows special characters such as ü
    # to show up correctly in the output. r.text returns unicode, but that didn't work for special chars
    page_source = r.content.decode("utf-8")
    #print("raw page_source", page_source)
    page_source = page_source.strip('\t\t').split('\n')
    #print("Length of page_source", len(page_source))

    count += 50

    #print("iterations ", iterations)
    iterations  += 1

    backloggery_backup = backloggery_backup + page_source
    backloggery_csv = []

    if(count >= 1000):
    #if(len(page_source) < 100):
    #if(count >= 3850):
        moreGames = False


        print("\nURL:", targetURL)
        print("--------------------------------------")

        print("Number of lines in the returned response: ", len(page_source))
        print("Number of games total", iterations*50)
        #print("Final page_source\n", page_source)

        print("--------------------------------------")

        #This works:
        print("len(backloggery_backup)", len(backloggery_backup))
        print("len(backloggery_backup[0])", len(backloggery_backup[0]))
        #print(backloggery_backup[0][:10])

        x = 0
        while x < len(backloggery_backup):

            currentLine = backloggery_backup[x].strip()
            #print(x, "\t", currentLine)

            parseLogic(currentLine)

            x += 1



   # Save the output to CSV

import csv

writepath = r'/Users/chrisnielsen/Documents/random-project-files/github-stage/backloggery-backup/backloggery_backup.csv'

try:
    with open(writepath, 'w') as outfile:
        writer = csv.writer(outfile, delimiter = ",")

        for row in gameDetailsMatrix:
            writer.writerow(row)

except:
    print("Write Error: Permission denied. Can't open", writepath)

print("Success! The file has been written here:", writepath)
