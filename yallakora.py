import os
import requests
from bs4 import BeautifulSoup
import csv
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# date = input('Please enter a date in the following format MM/DD/YYYY: ')
# page = requests.get(f'https://www.yallakora.com/match-center/?date={date}#')


def get_dates(start_date, end_date):
    list = []
    current_date = datetime.strptime(start_date,'%m/%d/%Y')
    while current_date <= datetime.strptime(end_date,'%m/%d/%Y'):
        list.append(current_date.strftime('%m/%d/%Y'))
        current_date += timedelta(days=1)
    # print(list)
    return list


    
    
    
    
def main():
    dates = get_dates("08/01/2023","08/10/2023")
    for i in dates:
        i = str(i)
        page = requests.get(f'https://www.yallakora.com/match-center/?date={i}#')
        
        
        src = page.content
        soup = BeautifulSoup(src, "lxml")
        matchs_details = []
        
        championships = soup.find_all('div', {'class': 'matchCard'})  # all championships and all matches
        
        def get_match_info(championships):
            championships_title = championships.contents[1].find('h2').text.strip()
            all_matches = championships.contents[3].find_all('li')  # list of all matches
            num_of_matches = len(all_matches)  # number of matches
            
            for i in range(num_of_matches):
                # get teams names
                team_A = all_matches[i].find('div', {'class': 'teamA'}).text.strip()
                team_B = all_matches[i].find('div', {'class': 'teamB'}).text.strip()
                
                # get score
                match_result = all_matches[i].find('div', {'class': 'MResult'}).find_all('span', {'class': 'score'})  # list of score
                score = f'{match_result[0].text.strip()} - {match_result[1].text.strip()}'  # string of score
                
                # get match time
                match_time = all_matches[i].find('div', {'class': 'MResult'}).find('span', {'class': 'time'}).text.strip() 
                
                # adding match info into match details
                matchs_details.append({'championship name': championships_title, 'first team': team_A, 'second team': team_B,
                                    'match time': match_time, 'match result': score})
        
        for i in range(len(championships)):
            get_match_info(championships[i])
            
        # Save data to MongoDB
        # Replace 'your_mongodb_uri' with your actual MongoDB URI
        client = MongoClient('mongodb://localhost:27017')
        db = client['sol']  # Replace 'your_database_name' with your desired database name
        collection = db['test7']  # Replace 'your_collection_name' with your desired collection name
        collection.insert_many(matchs_details)
        print('Data saved to MongoDB successfully!')
        
        # Save data to CSV (optional)
        keys = matchs_details[0].keys()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file_path = os.path.join(script_dir, 'matchesdetails.csv')

        with open(output_file_path, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(matchs_details)
            print('Data saved to CSV:', output_file_path)
            
            
            
        # Perform data analysis on MongoDB data
        data = list(collection.find({}))  # Retrieves all documents from the collection
        df = pd.DataFrame(data)
        print(df.describe())
            # Add the code for extracting and calculating average goals here
        def extract_goals(score_str):
            # Split the score string on '-' character and convert components to integers
            goals = [int(goal.strip()) for goal in score_str.split('-')]
            return goals

        # Convert the 'match result' column to a list of lists containing the goals for each team
        df['match result'] = df['match result'].apply(extract_goals)

        # Calculate the mean based on the extracted goals
        df['average_goals'] = df['match result'].apply(lambda x: sum(x) / len(x))

        # Now you can calculate the average score by championship using the 'average_goals' column
        average_score_by_championship = df.groupby('championship name')['average_goals'].mean()
        print(average_score_by_championship)
        
        # Data visualization
        average_score_by_championship.plot(kind='bar')
        plt.xlabel('Championship')
        plt.ylabel('Average Score')
        plt.title('Average Score by Championship')
        plt.show()
    

main()