import httpx
import os
import yaml
import io

from datetime import datetime

location_id = os.environ["FALLBACK_LOCATION_ID"] 
vendor_id = os.environ["FALLBACK_VENDOR_ID"] 
BASE_CATALOG_URL = os.environ['BASE_URL']+"/api/catalog"
BASE_RASA_URL = "localhost:5005/model/parse"
items = []
categories = []

item_parse_result = []

def test_menu_item():
    
    base_folder = create_test_directory()
    nlu = NLU(base_folder)
    nlu.test_nlu()

    core = Core(base_folder)
    core.test_core() 

    # nlu yaml file   


class NLU():
    def __init__(self, base_folder) -> None:
        self.case_1_results = {}
        self.case_2_results = {}
        self.case_3_results = {}
        self.base_folder = base_folder
        
  
    def test_nlu(self):
        dir_path = self.base_folder + "/results/nlu"
        try:
            get_items_from_square()
            combined_list = categories + items
            combined_examples = ''
            for item in combined_list:
                combined_examples += self.get_nlu_template(item)

            nlu_dict = self.get_nlu_yml_file(combined_examples)
            file_name = self.base_folder + "/test_files/test_nlu.yml"
            with io.open(file_name,"w") as file:
                yaml.dump(nlu_dict, file, default_flow_style=False, allow_unicode=True)
            
        except Exception as e:
            os.removedirs(dir_path)

    # def validate(self, output_dict, item_name):
    #     result_dict = {}
    #     intent = output_dict['intent']['name']
    #     entity_list = output_dict['entities'] 
    #     entity_check = False
    #     if len(entity_list) > 0:
    #         for ent in entity_list:
    #             if ent['entity'] == 'food' and ent['value'] == item_name:
    #                 entity_check = True

    #     if intent == 'request_order' and entity_check:
    #         result_dict[item_name] = "PASS"            
    #     else:
    #         result_dict[item_name] = "FAIL" 
    #     return result_dict

    # def test_case(self, item_name, item_prefix, result_dict):
    #     item_dict = { 'text': f"{item_prefix} {item_name}" } 
    #     item_json = json.dumps(item_dict)
    #     cmd = f"curl {BASE_RASA_URL} -d '{item_json}'"
    #     result =  self.get_output(cmd, item_name)  
    #     result_dict[item_name] = result[item_name]


    # def get_output(self , command, item_name):
    #     output_dict = self.parse_text_from_rasa(command)
    #     return self.validate(output_dict, item_name) 
    
    # def parse_text_from_rasa(self, command:str): 
    #     output_json = os.popen(command).read()
    #     output_dict = json.loads(output_json)
    #     return output_dict

    # def write_results_to_file(self, file_path, result_list:Dict[Text, Text], test_text_prefix):
    #     with open(file_path,'w') as file:
    #         json.dump(result_list, file)
    
    def get_nlu_template(self, item_name):
        example_string = '- [four](number) [plates](food_units) ['+item_name+'](food) \n- [i would like to add]{"entity": "cart_action", "group": "add"} [4](number) [plates](food_units) of ['+item_name+'](food) \n- [cancel]{"entity": "cart_action", "group": "remove"} [2](number) [plates](food_units) ['+item_name+'](food) \n- [please add]{"entity": "cart_action", "group": "add"} [one](number) [plate](food_units) ['+item_name+'](food) \n- [three](number) ['+item_name+'](food) \n- ['+item_name+'](food)   \n'
        return example_string
        
    def get_nlu_yml_file(self, combined_string):
        return {
            'version': '2.0',
            'nlu': [
                {
                    'intent': 'request_order',
                    'examples': combined_string
                }
            ]
        }

class Core():
    def __init__(self, base_folder) -> None:
        self.case_id_1_stories = []
        self.case_id_2_stories = []
        self.case_id_3_stories = []
        self.base_folder = base_folder

    def test_core(self):
        get_items_from_square()
        first_n_items = 2
        
        for i in range(0,len(categories)):
            if i == first_n_items:
                break
            story = self.get_category_template(categories[i])
            self.case_id_1_stories.append(story)
        
        for i in range(0,len(items)):
            if i == first_n_items:
                break
            item_story_2 = self.get_item_template_2(items[i])
            self.case_id_2_stories.append(item_story_2)
            item_story_3 = self.get_item_template_3(items[i])
            self.case_id_3_stories.append(item_story_3)

        case_id_1_to_serialize = {
            'stories': self.case_id_1_stories
        }
        case_id_2_to_serialize = {
            'stories': self.case_id_2_stories
        }
        case_id_3_to_serialize = {
            'stories': self.case_id_3_stories
        }
        story_base_folder, result_folder_name = self.create_core_directories(case_id_1_to_serialize, case_id_2_to_serialize, case_id_3_to_serialize) 
        # res = os.popen(f'rasa test core --stories {story_base_folder} --out {result_folder_name}').read()

    def create_core_directories(self, case_id_1_to_serialize, case_id_2_to_serialize, case_id_3_to_serialize):
        
        case_1_story_file_name =  self.base_folder + "/test_files/test_case_1.yml"
        case_2_story_file_name =  self.base_folder + "/test_files/test_case_2.yml"
        case_3_story_file_name =  self.base_folder + "/test_files/test_case_3.yml"

        story_base_folder = self.base_folder + "/test_files/"
        result_folder_name =  self.base_folder + "/results/core"

        with io.open(case_1_story_file_name,"w") as file:
            yaml.dump(case_id_1_to_serialize, file, default_flow_style=False, allow_unicode=True)

        with io.open(case_2_story_file_name,"w") as file:
            yaml.dump(case_id_2_to_serialize, file, default_flow_style=False, allow_unicode=True)

        with io.open(case_3_story_file_name,"w") as file:
            yaml.dump(case_id_3_to_serialize, file, default_flow_style=False, allow_unicode=True) 
        
        return story_base_folder, result_folder_name
    
    

    def get_category_template(self, category_name):
        category_dict = {   
            'story': 'test category '+ category_name,
            'steps': [
                {
                    'intent': 'request_order',
                    'user': '[add]{"entity": "cart_action", "group": "add"} [2](number) [plates](food_units) ['+ category_name +'](food)',
                },
                {'slot_was_set': [{'cart_action': 'add'}]},
                {'action': 'restaurant_form'},
                {'active_loop': 'restaurant_form'},
                {'slot_was_set': [{'cart_action': 'add'}]},
                {'slot_was_set': [{'units': 'plate'}]},
                {'slot_was_set': [{'item': None}]},
                {'slot_was_set': [{'quantity': 2}]},
                {'slot_was_set': [{'units': 'plates'}]},
                {'slot_was_set': [{'requested_slot': 'item'}]},
            ],
        }  
        # return json.dumps(category_dict)
        return category_dict

    def get_item_template_2(self, item_name):
        return {
            'story': 'Case id 2 (2 plates '+ item_name +')',
            'steps': [
                {
                    'intent': 'request_order',
                    'user': '[2](number) [plates](food_units) ['+ item_name +'](food)',
                },
                {'action': 'restaurant_form'},
                {'active_loop': 'restaurant_form'},
                {'slot_was_set': [{'cart_action': 'add'}]},
                {'slot_was_set': [{'units': 'plate'}]},
                {'slot_was_set': [{'item': f'{ item_name }'}]},
                {'slot_was_set': [{'quantity': 2}]},
                {'slot_was_set': [{'units': 'plates'}]},
                {'slot_was_set': [{'requested_slot': None}]},
                {'active_loop': None},
                {'action': 'action_place_order'},
                {'action': 'utter_submit'},
            ],
        }
        
    def get_item_template_3(self, item_name):
        return {
            'story': 'Case id 3 (order '+ item_name +' with follow up number)',
            'steps': [
                {
                    'intent': 'request_order',
                    'user': '[Order]{"entity": "cart_action", "group": "add"} [' + item_name +'](food)',
                },
                {'slot_was_set': [{'cart_action': 'Order'}]},
                {'action': 'restaurant_form'},
                {'active_loop': 'restaurant_form'},
                {'slot_was_set': [{'cart_action': 'Order'}]},
                {'slot_was_set': [{'units': 'plate'}]},
                {'slot_was_set': [{'item': f'{ item_name }'}]},
                {'slot_was_set': [{'requested_slot': 'quantity'}]},
                {'intent': 'request_order', 'user': '[2](number) [plates](food_units)'},
                {'action': 'restaurant_form'},
                {'slot_was_set': [{'units': 'plates'}]},
                {'slot_was_set': [{'quantity': 2}]},
                {'slot_was_set': [{'requested_slot': None}]},
                {'active_loop': None},
                {'action': 'action_place_order'},
                {'action': 'utter_submit'},
            ],
        }

def get_items_from_square():
    result = httpx.get(BASE_CATALOG_URL, params={
            'location_id': location_id,
            'vendor_id': vendor_id
        })
    res = result.json()['objects']
    for item in res:
        if 'category_data' in item:
            categories.append(item['category_data']['name'])
        elif 'item_data' in item:
            items.append(item['item_data']['name'])

def create_test_directory():
        folder_name = location_id+"_"+str(datetime.now().strftime('%Y%m%d%H%M%S'))
        base_folder = './tests/'+ folder_name
        result_path_core =  base_folder + "/results/core"
        result_path_nlu =  base_folder + "/results/nlu"
        file_path =  base_folder + "/test_files"
        if not os.path.exists(result_path_core):
            os.makedirs(result_path_core)
        if not os.path.exists(result_path_nlu):
            os.makedirs(result_path_nlu)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        return base_folder


    

test_menu_item()