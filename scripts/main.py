import looker_sdk
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Creating the looker SDK object to make a connection to Looker API
sdk = looker_sdk.init40()
start_time = datetime.now()
# Dict with ids which we do not check for a week
seven_days_do_not_check_dict = {'2024-03-15': ['2028',
                                               '2029',
                                               '2000',
                                               '1978',
                                               '2139',
                                               '2107',
                                               '2222',
                                               '2186',
                                               '2337'],
                                '2024-03-18': ['1371',
                                               '1361',
                                               '1906',
                                               '2315'],
                                '2024-03-19': ['1898',
                                               '2051']}


# function to check is the period of waiting for the id is over or not
def do_not_need_for_a_week(id):
    for date in seven_days_do_not_check_dict:
        if (datetime.now() - (datetime.strptime(date, "%Y-%m-%d"))).days < 8:
            if id in seven_days_do_not_check_dict[date]:
                return True
    else:
        return False


# Function for checking the response from the database by keywords in single dashboard
def single_dashboard_check(id: str):
    # print('board - ' + id, end=' | ')
    if do_not_need_for_a_week(id):
        return f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id} ✅"
    try:
        board = sdk.dashboard(dashboard_id=id)
        error_words = ('error', 'Error', 'trouble', 'Trouble')
        for tile in board.dashboard_elements:
            if getattr(tile, 'query', None) is not None and getattr(tile.query, 'id', None) is not None:
                query = tile.query
                if query and query.id:
                    query_response = sdk.run_query(query_id=query.id, result_format='json')
                    if any(word in query_response for word in error_words):
                        return f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id} ❌"
        return f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id} ✅"
    except:
        return f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id} ❌"


# Function for checking the response from the database by keywords in single look
def single_look_check(id: str):
    # print('look - ' + id, end=' | ')
    if do_not_need_for_a_week(id):
        return f"https://bigfishgames.gw1.cloud.looker.com/looks/{id} ✅"
    try:
        look = sdk.look(look_id=id)
        error_words = ('error', 'Error', 'trouble', 'Trouble')
        query = look.query
        if query and query.id:
            query_response = sdk.run_query(query_id=query.id, result_format='json')
            if any(word in query_response for word in error_words):
                return f"https://bigfishgames.gw1.cloud.looker.com/looks/{id} ❌"
        return f"https://bigfishgames.gw1.cloud.looker.com/looks/{id} ✅"
    except:
        return f"https://bigfishgames.gw1.cloud.looker.com/looks/{id} ❌"


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
        if 'archive' not in folder.name.lower() and 'DEV' not in folder.name:
            get_dashboards_in_folder(folder.id, dict_of_ids)


result_txt_list = []  # Variable for Slack message


# Function for enumerating all dashboards and looks in a folder and checking them out
def check_all_dashboards_and_looks_in_folder(folder_id, result_xtx_name, folder_name):
    dict_of_dashboards_and_looks = {'dashboards': [], 'looks': []}
    get_dashboards_in_folder(folder_id, dict_of_dashboards_and_looks)

    for board in dict_of_dashboards_and_looks['dashboards']:
        result = single_dashboard_check(board)
        if "❌" in result:
            result_txt_list.append(result)

    for look in dict_of_dashboards_and_looks['looks']:
        result = single_look_check(look)
        if "❌" in result:
            result_txt_list.append(result)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current time selection
    end_time = datetime.now()
    duration = end_time - start_time
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    file_path = f'results/{result_xtx_name}.txt'

    # Population the executive_kpi_result.txt file to send it into Slack
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"# Results at {now}:\n\n")
        file.write('- ' + f'{folder_name}' + '\n')
        if not result_txt_list:
            file.write('All is GOOD!\n')
        else:
            for link in result_txt_list:
                file.write(link + '\n')

        file.write(f"\nTime spent on task: {hours} hours and {minutes} minutes.\n")

# Dict with folders that need to be checked (un-comment on existing ones or add new ones by analogy)
# folders_dict = {
#     'Executive KPIs': '1121',
#     'Cohort LTV KPIs': '333',
#     'Ad Monetization': '400',
#     'Finance': '655',
#     'All Games': '399',
#     'Premium Games': '786',
#     'Blast Explorers': '889',
#     'Cooking Craze': '59',
#     'Evermerge': '870',
#     'Fairway': '1128',
#     'Fashion Crafters': '763',
#     'Gummy Drop!': '58',
#     'Match Upon a Time': '1035',
#     'Puzzles and Passports': '1161',
#     'Towers & Titans': '844',
#     'Travel Crush': '1074',
#     'Ultimate Survivors': '1043',
#     'Manta Ray': '688'
#
# }
