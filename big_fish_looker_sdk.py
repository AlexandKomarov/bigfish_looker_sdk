import looker_sdk
from datetime import datetime

# Creating the looker SDK object to make a connection to Looker API
sdk = looker_sdk.init40()


# Function for checking the response from the database by keywords in single dashboard
def single_dashboard_check(id: str, result_dict: dict):
    try:
        board = sdk.dashboard(dashboard_id=id)
        error_words = ('error', 'Error', 'trouble', 'Trouble')
        for tile in board.dashboard_elements:
            query = tile.query
            if query and query.id:
                query_response = sdk.run_query(query_id=query.id, result_format='json')
                if any(word in query_response for word in error_words):
                    result_dict['bad'].append(f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id} ❌")
                    break
        else:
            result_dict['good'].append(f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id} ✅")
    except:
        result_dict['bad'].append(f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id} ❌")


# Function for checking the response from the database by keywords in single look
def single_look_check(id, result_dict: dict):
    try:
        look = sdk.look(look_id=id)
        error_words = ('error', 'Error', 'trouble', 'Trouble')
        query = look.query
        if query and query.id:
            query_response = sdk.run_query(query_id=query.id, result_format='json')
            if any(word in query_response for word in error_words):
                result_dict['bad'].append(f"https://bigfishgames.gw1.cloud.looker.com/looks/{id} ❌")
            else:
                result_dict['good'].append(f"https://bigfishgames.gw1.cloud.looker.com/looks/{id} ✅")
    except:
        result_dict['bad'].append(f"https://bigfishgames.gw1.cloud.looker.com/look/{id} ❌")


# Function to retrieve all dashboards and looks in a folder using recursion
def get_dashboards_in_folder(folder_id, dict_of_ids):
    dashboards = sdk.folder_dashboards(folder_id)
    for dashboard in dashboards:
        dict_of_ids['dashboards'].append(dashboard.id)

    looks = sdk.folder_looks(folder_id)
    for look in looks:
        dict_of_ids['looks'].append(look.id)

    subfolders = sdk.folder_children(folder_id)
    for folder in subfolders:
        if 'archive' not in folder.name.lower() or 'DEV' != folder.name.lower():
            get_dashboards_in_folder(folder.id, dict_of_ids)


# Function for enumerating all dashboards and looks in a folder and checking them out
def check_all_dashboards_and_looks_in_folder(folder_id, result_dict):
    dict_of_dashboards_and_looks = {'dashboards': [], 'looks': []}
    get_dashboards_in_folder(folder_id, dict_of_dashboards_and_looks)

    for id in dict_of_dashboards_and_looks['dashboards']:
        single_dashboard_check(id, result_dict)

    for id in dict_of_dashboards_and_looks['looks']:
        single_look_check(id, result_dict)


# Dict with folders that need to be checked (un-comment on existing ones or add new ones by analogy)
folders_dict = {
    # 'Executive KPIs': '1121',
    # 'Cohort LTV KPIs': '333',
    # 'Ad Monetization': '400',
    # 'All Games': '399',
    # 'Blast Explorers': '889',
    # 'Cooking Craze': '59',
    # 'Evermerge': '870',
    # 'Fairway': '1128',
    # 'Fashion Crafters': '763',
    # 'Gummy Drop!': '58',
    # 'Match Upon a Time': '1035',
    'Puzzles and Passports': '1161',
    # 'Towers & Titans': '844',
    # 'Travel Crush': '1074',
    # 'Ultimate Survivors': '1043'
}

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time selection

file_path_readme = 'README.md'  # Path to README file

result_txt_dict = {}  # Variable for Slack message

# Population the README file
new_content = f"# Last results at {now} UTC:\n"
for folder in folders_dict:
    print(folder + 'START')
    result_dict = {'good': [], 'bad': []}
    result_txt_dict[folder] = []
    new_content += f'\n### {folder}: \n'
    check_all_dashboards_and_looks_in_folder(folders_dict[folder], result_dict)
    if not result_dict['bad']:
        new_content += '- All is GOOD!\n'
    else:
        for link in result_dict['bad']:
            new_content += f'- [{link}]({link[:-2]})\n'
            result_txt_dict[folder].append(link)
    print(folder + 'END')
with open(file_path_readme, 'w', encoding='utf-8') as file:
    file.write(new_content + '\n')

file_path = 'result.txt'

# Population the result.txt file to send it into Slack
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(f"# Results at {now}:\n\n")
    for folder in result_txt_dict:
        file.write('- ' + folder + '\n')
        if not result_txt_dict[folder]:
            file.write('All is GOOD!\n')
        else:
            for link in result_txt_dict[folder]:
                file.write(link + '\n')
