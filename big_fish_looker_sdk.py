import looker_sdk
import json
from datetime import datetime

sdk = looker_sdk.init40()

result_dict = {'good': [], 'bad': []}

def single_dashboard_check(id: str, result_dict: dict):
    try:
        board = sdk.dashboard(dashboard_id=id)
        error_words = ('error', 'Error', 'trouble', 'Trouble')
        for tile in board.dashboard_elements:
            query = tile.query
            if query and query.id:
                query_response = sdk.run_query(query_id=query.id, result_format='json')
                if any(word in query_response for word in error_words):
                    result_dict['bad'].append(f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id}")
                    break
        else:
            result_dict['good'].append(f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id}")
    except:
        result_dict['bad'].append(f"https://bigfishgames.gw1.cloud.looker.com/dashboards/{id}")


def single_look_check(id, result_dict: dict):
    try:
        look = sdk.look(look_id=id)
        error_words = ('error', 'Error', 'trouble', 'Trouble')
        query = look.query
        if query and query.id:
            query_response = sdk.run_query(query_id=query.id, result_format='json')
            if any(word in query_response for word in error_words):
                result_dict['bad'].append(f"https://bigfishgames.gw1.cloud.looker.com/looks/{id}")
            else:
                result_dict['good'].append(f"https://bigfishgames.gw1.cloud.looker.com/looks/{id}")
    except:
        result_dict['bad'].append(f"https://bigfishgames.gw1.cloud.looker.com/look/{id}")

single_dashboard_check('2180', result_dict)
single_look_check('2539', result_dict)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

new_content = f"# Results at {now}:\n\n"
new_content += '## Good\n'
for link in result_dict['good']:
    new_content += f'- [{link}]({link}) ✅\n'
new_content += '\n## Bad\n'
for link in result_dict['bad']:
    new_content += f'- [{link}]({link}) ❌\n'

file_path = 'README.md'

try:
    with open(file_path, 'r') as file:
        old_content = file.read()
except FileNotFoundError:
    old_content = ''

with open(file_path, 'w') as file:
    file.write(new_content + '\n' + old_content)