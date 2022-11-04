import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re
import numpy
# Max rows stored before dumping
THRESHOLD = 100

# Current page on site
page = 1

# Request header
HEADERS = {'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}

# Data columns stored
main_time = []
main_side_time = []
complete_time = []
all_styles_time = []
platform = []
genre = []
developer = []
publisher = []
retirement = []
rating = []
title = []
na = []
eu = []
jp = []

# Mode used to dump file, changes through execution
mode = "w"

def write_out():
    """
    Writes scraped data to an output file, if w mode is detected, if first write is detected,
    switches to append mode after writing
    """
    columns = {
        'Title': title,
        'Main_Time': main_time,
        'Main_Side_Time': main_side_time,
        'Complete_Time': complete_time,
        'All_Styles_Time': all_styles_time,
        'Platform': platform,
        'Genre': genre,
        'Developer': developer,
        'Publisher': publisher,
        'Retirement': retirement,
        'Rating': rating,
        'NA': na,
        'EU': eu,
        'JP': jp
    }
    df = pd.DataFrame(columns)

    # Changed output file logic
    outfile = os.path.join(os.path.abspath("."), "howlongtobeat.csv")
    
    saved = False
    while not saved:
        try:
            df.to_csv(outfile, sep=",", encoding='utf-8', index=False, mode='a', header=False) # Now outputs to the current directory
            saved = True
        except Exception as e:
                print("IO error has occured, sleeping for 5 seconds. Close the output file if open, Description is below")
                print(e)
                time.sleep(5)
    print("Saved to {outfile}".format(outfile=outfile))
    

def flush_buffer():
    """
    Flushes out write buffers
    """
    global main_time, main_side_time, complete_time, all_styles_time, platform, genre, developer, publisher, retirement, rating, title, na, eu, jp
    main_time = []
    main_side_time = []
    complete_time = []
    all_styles_time = []
    platform = []
    genre = []
    developer = []
    publisher = []
    retirement = []
    rating = []
    title = []
    na = []
    eu = [] 
    jp = []
    

# Check the dump file does not already exists    
outfile = os.path.join(os.path.abspath("."), "howlongtobeat.csv")
if os.path.exists(outfile):
        print(f"{outfile} already exists, please remove it before running the program!")
        exit()
saved = False

# Dump column header data to file
while not saved:
    try:
        columns = {
        'Title':title,
        'Main_Time': main_time,
        'Main_Side_Time': main_side_time,
        'Complete_Time': complete_time,
        'All_Styles_Time': all_styles_time,
        'Platform': platform,
        'Genre': genre,
        'Developer': developer,
        'Publisher': publisher,
        'Retirement': retirement,
        'Rating': rating,
        'NA': na,
        'EU': eu,
        'JP': jp
    }
        df = pd.DataFrame(columns)
        df = df[[
            'Title', 'Main_Time', 'Main_Side_Time', 'Complete_Time', 'All_Styles_Time', 'Platform',
            'Genre', 'Developer', 'Publisher', 'Retirement',
            'Rating', 'NA', 'EU', 'JP']]
        df.to_csv(outfile, sep=",", encoding='utf-8', index=False, mode='a') # Now outputs to the current directory
        saved = True
    except Exception as e:
        print("IO error has occured, sleeping for 5 seconds. Close the output file if open, Description is below")
        print(e)
        time.sleep(5)

# Parse each page until http code == 404
req = requests.get(f"https://howlongtobeat.com/game/{page}", headers=HEADERS)

for _ in range(0, 68151):
    if req.status_code < 400:
        # Get times 
        soup = BeautifulSoup(req.text, 'html.parser')
        parsed = soup.find_all("li", class_= lambda v: v and "GameStats_short__mnFjd time_" in v)
        
        # Process only pages with 4 times in
        if(len(parsed) == 4):
            print(f"Processing: https://howlongtobeat.com/game/{page}")
            # Process game times
            # Process each time separately
            for counter, line in enumerate(parsed):
                processed = line.find("h5").text.split()[0].replace('½', '.5')
                match counter:
                    case 0:
                        main_time.append(processed)
                    case 1:
                        main_side_time.append(processed)
                    case 2:
                        complete_time.append(processed)
                    case 3: 
                        all_styles_time.append(processed)
                        
        
            # Process platform, genre, developer, and publisher    
            parser = soup.find_all("div", {"class":"GameSummary_profile_info__e935c GameSummary_medium__5cP8Y"})
            
            if len(parser) >= 4:
            
                for i in range(0,4):
                    processed = parser[i].text.partition(" ")[2]
                    
                    match i:
                        case 0:
                            platform.append(processed)
                        case 1:
                            genre.append(processed)
                        case 2:
                            developer.append(processed)
                        case 3: 
                            publisher.append(processed)
            else:
                platform.append(numpy.NaN)
                genre.append(numpy.NaN)
                developer.append(numpy.NaN)
                publisher.append(numpy.NaN)
            
            # Process retirement info, can be NaN
            parser = soup.find("h5", {"style":"margin-top:-75px;text-align:center"})
            if not parser:
                retirement.append(numpy.NaN) 
            else:
                retirement.append(re.sub("[^0-9|.]", "",parser.text))
            
            # Process rating info, can be NaN
            parser = soup.find("h5", {"style":"margin-top:-67px;text-align:center"})
            if not parser:
                rating.append(numpy.NaN)
            else:
                rating.append(re.sub("[^0-9|.]", "",parser.text))
            
            # Process title
            title.append(soup.find("title").text[12:].partition('?')[0])
            
            # Process Release Date
            parser = soup.find_all("div", {"class":"GameSummary_profile_info__e935c"})

            for line in parser:
                key = line.text.partition(':')
                match key[0]:
                    case "NA":
                        na.append(key[2])
                    case "EU":
                        eu.append(key[2])
                    case "JP":
                        jp.append(key[2])
            
            if len(na) < len(title):
                na.append(numpy.NaN)
            if len(jp) < len(title):
                jp.append(numpy.NaN)
            if len(eu) < len(title):
                eu.append(numpy.NaN)


        else:
            print(f"Skipping: https://howlongtobeat.com/game/{page}")
        
        # Dump file if sufficient 
        if(len(title) >= THRESHOLD):
            write_out()
            flush_buffer()
    else:
        print(f"404: https://howlongtobeat.com/game/{page}")
    
    # Increment and get next page
    page += 1
    req = requests.get(f"https://howlongtobeat.com/game/{page}", headers=HEADERS)

# Final flush
write_out()
flush_buffer()