from datetime import datetime
from typing import Union, List, Tuple, Any

import httpx
import pytz
from rasa_sdk import Tracker

from actions import config
from actions.config import BASE_CATALOG_URL, BASE_ORDER_URL, CART_URL, BASE_URL
from actions.utils.time_utils import parse_period

ADDRESS_FORMAT = "{address_line_1}, {locality}, {administrative_district_level_1} {postal_code}, {country}"
ADDRESS_FORMAT_WITHOUT_ADL1 = "{address_line_1}, {locality}, {postal_code}, {country}"


def resolve_item_from_variant(res_variant, items):
    if res_variant is None or items is None:
        return None

    for item in items:
        for variant in item['item_data']['variations']:
            if variant['id'] == res_variant['id']:
                return item

    return None


def resolve_category_from_item(res_item, categories):
    if res_item is None or categories is None:
        return None

    for category in categories:
        if category['id'] == res_item['item_data']['category_id']:
            return category

    return None


class Square:
    def __init__(self, tracker: Tracker):
        _metadata = tracker.latest_message.get("metadata")
        if _metadata.get('instaline') and _metadata.get('instaline').get('location'):
            self.location = _metadata.get('instaline').get('location')
        elif tracker.get_latest_input_channel() == 'instaline':
            raise ValueError("location metadata is required.")
        else:
            self.location = config.FALLBACK_LOCATION_ID

        if _metadata.get('instaline') and _metadata.get('instaline').get('vendor'):
            self.vendor = _metadata.get('instaline').get('vendor')
        elif tracker.get_latest_input_channel() == 'instaline':
            raise ValueError("vendor metadata is required.")
        else:
            self.vendor = config.FALLBACK_VENDOR_ID

    def get_catalog(self):
        return httpx.get(BASE_CATALOG_URL, params={
            'location_id': self.location,
            'vendor_id': self.vendor
        })

    def menu_item_exists(self, item_name: str):
        res = httpx.get(BASE_CATALOG_URL + f"/search/{item_name}", params={
            'location_id': self.location,
            'vendor_id': self.vendor
        }, timeout=30)
        return res.json() if res.status_code == httpx.codes.OK else {'objects': []}

    def match_menu_item(self, item: str):
        pass

    def create_order(self, item, quantity, user_id):
        headers = {
            "accept": "application/json",
            "cache-control": "no-cache",
            "content-type": "application/json",
        }

        data = {
            "user_id": str(user_id),
            "items": [{"id": item['item_data']['variations'][0]["id"], "quantity": quantity}],
        }

        response = httpx.post(f"{BASE_ORDER_URL}/create", headers=headers, json=data, params={
            'location_id': self.location,
            'vendor_id': self.vendor
        })

        # Return total amount
        # Order id
        return response.json()

    # def add_notes(self, user_id, notes):
    #     get_cart_id = httpx.get(url=CART_ID_URL + user_id, params={
    #         'location_id': self.location,
    #         'vendor_id': self.vendor
    #     })
    #     response = get_cart_id.json()
    #     if len(response) > 0:
    #         res = response[0]
    #         response_user_id = res['user_id']
    #         if response_user_id == user_id:
    #             # previous_item = res['items'][-1]
    #             res['items'][-1]['notes'] = notes
    #         data = {
    #             "client_modified": datetime.now().isoformat(),
    #             "id": res['id'],
    #             "items": res['items']
    #         }
    #         response = httpx.post(url=CART_URL + user_id, json=data, timeout=30, params={
    #                     'location_id': self.location,
    #                     'vendor_id': self.vendor
    #                     })
    #         return response.json()

    def save_to_cart(self, item, quantity, user_id):
        get_cart_id = httpx.get(url=CART_URL + user_id, params={
            'location_id': self.location,
            'vendor_id': self.vendor
        })

        res = get_cart_id.json()
        # print("cart id response")
        # print(res)

        if not get_cart_id.is_error and res:
            cart = res
            cart_id = cart['id']
            cart_items = cart['items']

            catalog_item_id = item['id']
            catalog_variation_id = item['item_data']['variations'][0]["id"]
            display_name = item['item_data']['name']
            try:
                int_quantity = int(quantity)
            except Exception as e:
                raise e
            for each_item in cart_items:
                if each_item['catalog_variation_id'] == catalog_variation_id:
                    each_item['quantity'] = each_item['quantity'] + int_quantity
                    int_quantity = 0
                    break

            if int_quantity > 0:
                value = {
                    "catalog_item_id": catalog_item_id,
                    "catalog_variation_id": catalog_variation_id,
                    "display_name": display_name,
                    "notes": "more soup",
                    "quantity": quantity
                }
                cart_items.append(value)
            data = {
                "client_modified": datetime.now().isoformat(),
                "id": cart_id,
                "items": cart_items
            }

        else:
            if get_cart_id.is_error and get_cart_id.status_code != 404:
                raise Exception(get_cart_id.json())
            data = {
                "client_modified": datetime.now().isoformat(),
                "items": [
                    {
                        "catalog_item_id": item['id'],
                        "catalog_variation_id": item['item_data']['variations'][0]["id"],
                        "display_name": item['item_data']['name'],
                        "notes": "more soup",
                        "quantity": quantity
                    }
                ],
            }
        # print("data")
        # print(data)
        response = httpx.post(url=CART_URL + user_id, json=data, timeout=30, params={
            'location_id': self.location,
            'vendor_id': self.vendor
        })
        return response.json()

    def remove_from_cart(self, item, quantity, user_id):
        get_cart_id = httpx.get(url=CART_URL + user_id, params={
            'location_id': self.location,
            'vendor_id': self.vendor
        })

        res = get_cart_id.json()
        # print("cart id response")
        # print(res)

        if res:
            cart = res
            cart_id = cart['id']
            cart_items = cart['items']

            catalog_item_id = item['id']
            catalog_variation_id = item['item_data']['variations'][0]["id"]
            try:
                int_quantity = int(quantity)
            except Exception as e:
                raise e
            for pos, each_item in enumerate(cart_items):
                if each_item['catalog_item_id'] == catalog_item_id \
                        and each_item['catalog_variation_id'] == catalog_variation_id:
                    each_item['quantity'] = each_item['quantity'] - int_quantity
                    if each_item['quantity'] <= 0:
                        each_item['quantity'] = 0
                        # del cart_items[pos]
                    int_quantity = 0
                    break

            # if int_quantity > 0:
            #     value = {
            #         "catalog_item_id": catalog_item_id,
            #         "catalog_variation_id": catalog_variation_id,
            #         "display_name": display_name,
            #         "notes": "more soup",
            #         "quantity": quantity
            #     }
            #     cart_items.append(value)
            data = {
                "client_modified": datetime.now().isoformat(),
                "id": cart_id,
                "items": cart_items
            }

            # else:
            #     data = {
            #         "client_modified": datetime.now().isoformat(),
            #         "items": [
            #             {
            #                 "catalog_item_id": item['id'],
            #                 "catalog_variation_id": item['item_data']['variations'][0]["id"],
            #                 "display_name": item['item_data']['name'],
            #                 "notes": "more soup",
            #                 "quantity": quantity
            #             }
            #         ],
            #     }
            # print("data")
            # print(data)
            # response = httpx.post(url=cart_url, data=data, headers={'Authorization': 'Bearer {}'.format(generate_token())})
            response = httpx.post(url=CART_URL + user_id, json=data, timeout=30, params={
                'location_id': self.location,
                'vendor_id': self.vendor
            })
            # print(response.json())
            return response.json()
        else:
            return []

    def show_location(self):
        # loc_endpoint = base_url + "/api/location/L08KM4B56KJK1"
        loc_endpoint = BASE_URL + "/api/location/" + self.location
        req = httpx.get(loc_endpoint, params={
            'location_id': self.location,
            'vendor_id': self.vendor
        })
        res = req.json()
        data = res['location']['address']
        if 'administrative_district_level_1' in data:
            address = ADDRESS_FORMAT.format(**data)
        else:
            address = ADDRESS_FORMAT_WITHOUT_ADL1.format(**data)
        return address

    def get_location_data(self):
        # loc_endpoint = base_url + "/api/location/L08KM4B56KJK1"
        loc_endpoint = BASE_URL + "/api/location/" + self.location
        req = httpx.get(loc_endpoint, params={
            'location_id': self.location,
            'vendor_id': self.vendor
        })
        res = req.json()
        return res

    def get_business_hours_formatted(self):
        location_data = self.get_location_data()
        data = location_data['location']['business_hours']['periods']
        location_tz = pytz.timezone(location_data['location']['timezone'])

        str_shown = ""
        for item in data:
            start = parse_period(item['start_local_time'], location_tz, item['day_of_week'])
            start_str = start.strftime('%H:%M')

            end = parse_period(item['end_local_time'], location_tz, item['day_of_week'])
            end_str = end.strftime('%H:%M')

            period = item['day_of_week'] + " " + start_str + "-" + end_str + "|\n"
            str_shown = str_shown + period
        return str_shown

    def resolve_item_slot(self, item_slot: Union[str, List[str]]) -> Tuple[Any, Any, Any, Any]:
        """
        1. If there is one item variant, pick that item variant
        2. If only one item pick item
        3. If there is one category pick the category
        4. Ask the user to rephrase

        User queries
        1. Categories
            - Ask for item and item variant
        2. Items
            - We ask for item variant / modifier
            - Move to the next step (quantity etc...)
        3. Item Variant
            - If there is one item variant, choose it as default
            - Confirm Add variant instead?

        :param item_slot: the item to resolve
        :return: returns Tuple(Category, Item, Variant, Options)

        return
        """

        if isinstance(item_slot, List):
            item_to_resolve = " ".join(item_slot)
        elif isinstance(item_slot, str):
            item_to_resolve = item_slot
        else:
            item_to_resolve = str(item_slot)

        result = self.menu_item_exists(item_to_resolve)
        if 'objects' not in result:
            return None, None, None, None
        res = result["objects"]

        variants = [x for x in res if x["type"] == "ITEM_VARIATION"]
        items = [x for x in res if x["type"] == "ITEM"]
        categories = [x for x in res if x["type"] == "CATEGORY"]

        res_variant = None
        res_item = None
        res_category = None

        if len(variants) == 1:
            res_variant = variants[0]
        for variant in variants:
            if str(variant['item_variation_data']['name']).lower() == item_to_resolve.lower():
                res_variant = variant
                break
        if res_variant is not None:
            res_item = resolve_item_from_variant(res_variant, items)
            res_category = resolve_category_from_item(res_item, categories)

            return res_variant, res_item, res_category, None

        if len(items) == 1:
            res_item = items[0]
        for item in items:
            if str(item['item_data']['name']).lower() == item_to_resolve.lower():
                res_item = item
                break
        if res_item is not None:
            res_category = resolve_category_from_item(res_item, categories)
            if len(res_item['item_data']['variations']) == 1:
                res_variant = items[0]['item_data']['variations'][0]
                return res_variant, res_item, res_category, None
            return res_variant, res_item, res_category, res_item['item_data']['variations']

        if len(categories) == 1:
            res_category = categories[0]
        for category in categories:
            if str(category['category_data']['name']).lower() == item_to_resolve.lower():
                res_category = category
                break
        if res_category is not None:
            category_items = [x for x in items if x['item_data']['category_id'] == res_category["id"]]
            if len(category_items) == 1:
                res_item = category_items[0]
                if len(res_item['item_data']['variations']) == 1:
                    res_variant = items[0]['item_data']['variations'][0]
                    return res_variant, res_item, res_category, None
            return res_variant, res_item, res_category, category_items

        res_options = []
        if len(variants) > 1:
            res_options.extend(variants)
        if len(items) > 1:
            res_options.extend(items)
        if len(categories) > 1:
            res_options.extend(categories)
        return res_variant, res_item, res_category, res_options if len(res_options) > 0 else None
