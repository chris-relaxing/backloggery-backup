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
raw_backloggery_backup = ""
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


def getCompilationGames(compName, currentLine):
    #print("Entering getCompilationGames", compName)
    global compilationName
    global system
    compilationName = compName

    # Parse this section for the system and compQueryName for the URL
    # getComp(2718,'XBLA','Namco+Museum%3A+Virtual+Arcade')">&#x25BC;</span>
    part1 = currentLine.split('getComp(')[1]
    queryParts = part1.split(')')[0].split(',')
    system = queryParts[1].replace("'", "")
    #compQueryName = queryParts[2]
    compQueryName = compName.replace(" ", "+")


    # Use the passed in compilation name to request the list of associated games
    #compQueryName = compName.replace(" ", "+")
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
        print(x, "-----\t\t", currentLine)
        parseLogic(currentLine)
        x += 1

    appendGameList(currentLine)
    compilationName = ""

def getCompilationNames(currentLine):
#     global system
    compilationName = currentLine.split('<')[0].strip()
    if compilationName != '&nbsp;':
        print("\nCompilation: ", compilationName)
        gameDetailsRow = currentConsole + "," + compilationName
        getCompilationGames(compilationName, currentLine)


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
    comments = comments.replace(",", "; ").replace('\n', " ")

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
    try:
        currentLine = currentLine.split('>')
        currentConsole = currentLine[3].split('<')[0]
    except:
        print("\n\n LAST CONSOLE. End of data.")


def appendGameList(currentLine):
    print("-------------------------------------------------")
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
    global comments

    # Get system for compilations
    # compURL https://backloggery.com/ajax_expandcomp.php?user=originalKILLJOY&comp_sys=<div class="gamerow">Completed 15 episodes.
    # [Ach. 4/12]</div></section><section class="gamebox">&comp=Namco+Museum:+Virtual+Arcade
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

    # Get the rest of the comments
    elif currentLine.endswith(','):
        commentListItem = currentLine.replace(',', '; ')
        comments += commentListItem

    # Get the rest of the comments, continued.. Last game in the list
    elif currentLine.endswith('</div></section>') and "gamerow" not in currentLine:
        commentListItem = currentLine.split('</div></section>')[0]
        comments += commentListItem + "; "

    # Part of a compilation?
    elif 'getComp(' in currentLine:
        getCompilationNames(currentLine)



moreGames = True
while moreGames:

    targetURL = "https://backloggery.com/ajax_moregames.php?user=" + backloggery_username + "&ajid=" + str(count)
    r = requests.get(targetURL)

    # Using r.content returns bytes, which works with decode and allows special characters such as ü
    # to show up correctly in the output. r.text returns unicode, but that didn't work for special chars
    page_source = r.content.decode("utf-8")
    page_source = page_source.strip('\t\t').split('\n')

    count += 50
    iterations  += 1

    backloggery_backup = backloggery_backup + page_source
    backloggery_csv = []

    #if(count >= 1000):
    #if(count >= 3850):
    # This line will collect the ENTIRE collection
    if(len(page_source) < 100):

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

        print("raw page_source", raw_backloggery_backup)

        x = 0
        while x < len(backloggery_backup):

            currentLine = backloggery_backup[x].strip()
            print(x, "\t", currentLine)

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





currentLine = """
<div class="gamecom-arrows" id="gamecomarr1002706" onclick="getComments(1002706)">&#x25BC; &#x25BC; &#x25BC;</div> <div id="comments1002706" class="gamerow" style="display: none; border: none;">1941 Counter Attack,
Avengers,
Black Tiger,
Block Block,
Captain Commando,
Eco Fighters,
King of Dragons,
Knights of the Round,
Last Duel,
Magic Sword,
Mega Twins,
Quiz &amp; Dragons: Capcom Quiz Game,
Side Arms Hyper Dyne,
Street Fighter,
Strider,
Super Street Fighter II Turbo,
The Speed Rumbler,
Three Wonders,
Tiger Road,
Varth: Operation Thunderstorm</div></section>
<section class="gamebox">
"""

if 'getComments' in currentLine:

    comments1 = ""
    comments2 = ""
    #comments = currentLine.split('>')[3].split('<')[0]
    splitLine = currentLine.split('getComments')
    part1 = splitLine[0]
    if "gamerow" in part1:
        comments1 = part1.split('"gamerow">')[1].split('<')[0] + "|"
    part2 = splitLine[1].replace('&#x25BC;', "").strip()
    comments2 = part2.split('>')[3].split('<')[0]
    comments = comments1 + comments2.strip()
    comments.replace(",", ";")

    print("Comments:", comments)
