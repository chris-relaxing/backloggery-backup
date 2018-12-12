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

TODO:
1. You can even download your friend's collections and make comparisons per console.
2. Idea: scrape Xbox game art images from xbox.com

"""
backloggery_username = "originalKILLJOY"
export_to_csv  = True
export_to_xlsx = True

count = 0
iterations = 1
backloggery_backup = ""

moreGames = True
while moreGames:

    targetURL = "https://backloggery.com/ajax_moregames.php?user=" + backloggery_username + "&ajid=" + str(count)
    #targetURL = "https://backloggery.com/ajax_moregames.php?user=originalKILLJOY&ajid=" + str(count)
    r = requests.get(targetURL)
    page_source = r.text
    #page_source = page_source.split('\n')
    print("Length of page_source", len(page_source))

    count += 50

    print("iterations ", iterations)
    iterations  += 1

    backloggery_backup = backloggery_backup + page_source

    if(len(page_source) < 100):
    #if(count >= 3850):
        moreGames = False


        print("\nURL:", targetURL)
        print("--------------------------------------")

        print("Number of lines in the returned response: ", len(page_source))
        print("Number of games total", iterations*50)
        print("Final page_source\n", page_source)

        print("--------------------------------------")

        #This works:
        #print(backloggery_backup)
