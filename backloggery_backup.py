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

TODO:
1. You can even download your friend's collections and make comparisons per console.
2. Idea: scrape Xbox game art images from xbox.com

"""
backloggery_username = "originalKILLJOY"
export_to_csv  = True
export_to_xlsx = True

count = 0
iterations = 1
# backloggery_backup = ""
backloggery_backup = []

gameDetails = []
moreGames = True
while moreGames:

    targetURL = "https://backloggery.com/ajax_moregames.php?user=" + backloggery_username + "&ajid=" + str(count)
    #targetURL = "https://backloggery.com/ajax_moregames.php?user=originalKILLJOY&ajid=" + str(count)
    r = requests.get(targetURL)
    page_source = r.text
    page_source = page_source.strip('\t\t').split('\n')
#     print("Length of page_source", len(page_source))

    count += 50

#     print("iterations ", iterations)
    iterations  += 1

    backloggery_backup = backloggery_backup + page_source
    backloggery_csv = []

    if(count >= 1000):
#     if(len(page_source) < 100):
    #if(count >= 3850):
        moreGames = False


        print("\nURL:", targetURL)
        print("--------------------------------------")

        print("Number of lines in the returned response: ", len(page_source))
        print("Number of games total", iterations*50)
#         print("Final page_source\n", page_source)

        print("--------------------------------------")

        #This works:
        print("len(backloggery_backup)", len(backloggery_backup))
        print("len(backloggery_backup[0])", len(backloggery_backup[0]))
#         print(backloggery_backup[0][:10])

        x = 0
        currentConsole = ""
        completionStatus = ""
        name = ""
        comments = ""
        achievements = ""
        while x < len(backloggery_backup):

            currentLine = backloggery_backup[x].strip()
            print(x, ".\t", currentLine)

            # Reached the beginning of a new game row
            if '<section class="gamebox">' in currentLine:
                print("-------------------------------------------------")
                gameDetailsRow = currentConsole   + "," + \
                                 completionStatus + "," + \
                                 name             + "," + \
                                 achievements     + "," + \
                                 comments
                gameDetailsRow.encode('UTF-8')
                if name:
                    gameDetails.append(gameDetailsRow)

                completionStatus = ""
                name = ""
                comments = ""
                achievements = ""

            # Get console
            elif 'class="gamebox systemend"' in currentLine:
                if currentLine.startswith('</section>'):
                    currentLine = currentLine[10:]
                currentLine = currentLine.split('>')
                currentConsole = currentLine[3].split('<')[0]
                print("\n\nConsole is:", currentConsole)

            # Get status
            elif 'alt="(' in currentLine:
                splitLine = currentLine
                completionStatus = splitLine.split('(')[1].split(')')[0]
                print("\nStatus is:", completionStatus)

                # Case of name on the same line as the status. For example:
                # <a href="games.php?user=originalkilljoy&amp;console=360&amp;status=2"><img alt="(B)"
                # width="16" height="16" src="images/beaten.gif" /></a> <b>Assassin's Creed</b>
                if "status=2" in currentLine or "status=3" in currentLine:
                    name = currentLine.split('<b>')[1].split('<')[0]


            # Get name
            elif currentLine.startswith('<b>') and currentLine.endswith('</b>'):
                cutoff = len(currentLine) - 4
                name = currentLine[3:cutoff]
                print("\nName is:", name)

            # Get achievements
            elif 'achievebar' in currentLine:
                part1 = currentLine.split('<table class="achievebar">')[0]
                achievements = part1.split('<b>')[1].replace('</b>', "")
                print(achievements)

            # Get comments
            elif 'getComments' in currentLine:
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

            # Part of a compilation?
            elif 'getComp(' in currentLine:
                compilation = currentLine.split('<')[0].strip()
                print("\nCompilation:", compilation)
                gameDetailsRow = currentConsole + "," + compilation
                gameDetails.append(gameDetailsRow)


            x += 1




# Test comments function --------

currentLine = """
<div class="gamerow">Beat the campaign on Normal</div><div class="gamecom-arrows" id="gamecomarr3018293"
onclick="getComments(3018293)">&#x25BC; &#x25BC; &#x25BC;</div> <div id="comments3018293"
class="gamerow" style="display: none; border: none;">Owned DLC: 1. Anniversary Map Pack; 2. Defiant Map Pack; 3. Noble Map Pack</div></section>
"""

currentLine = """
<div class="gamecom-arrows" id="gamecomarr12805652" onclick="getComments(12805652)">&#x25BC; &#x25BC; &#x25BC;</div> <div id="comments12805652" class="gamerow" style="display: none; border: none;">Nostromo Edition</div></section>
"""

comments1 = ""
comments2 = ""
if 'getComments' in currentLine:
#     comments = currentLine.split('>')[3].split('<')[0]
    splitLine = currentLine.split('getComments')
    part1 = splitLine[0]
    if "gamerow" in part1:
        comments1 = part1.split('"gamerow">')[1].split('<')[0] + "|"
    part2 = splitLine[1].replace('&#x25BC;', "").strip()
    comments2 = part2.split('>')[3].split('<')[0]
    print(part1)
    print('\n', part2)

    print('\n', comments1)
    print('\n', comments2)

    comments = comments1 + comments2
    comments.replace(",", ";")

    print('\n', comments)

# Test parsing of Achievements

currentLine = """
360</b> <span class="info"><img src="images/ribbon_0.gif" alt="" width="8" height="15" style="margin-top: 3px;" />
<span><b>Achievements:</b> 120 / 1000 (12%)<table class="achievebar"><tr><td style="width: 12%;" class="b"></td>
<td style="width: 88%;" class="bi"></td></tr></table></span></span>
"""

if 'achievebar' in currentLine:
    part1 = currentLine.split('<table class="achievebar">')[0]
    achievements = part1.split('<b>')[1].replace('</b>', "")
    print(achievements)



# Test unicode

import sys
# sys.setdefaultencoding("utf-8")
print(sys.getdefaultencoding())

text = 'Xbox 360,U,Brütal Legend,,'.encode('UTF-8')

print(text.decode('UTF-8'))
