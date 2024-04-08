import random
import re




import asyncio
import datetime
import time
import requests


def remove_duplicates(dict_list):
    seen = set()
    new_list = []
    for d in dict_list:
        frozen_dict = frozenset(d.items())
        if frozen_dict not in seen:
            seen.add(frozen_dict)
            new_list.append(d)
    return new_list


class PxqShowMonitor:
    def __init__(self):
        self.http = requests.Session()
        ua = ('Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
              'Version/16.6 Mobile/15E148 Safari/604.1')
        self.http.headers.update({
            'User-Agent': ua,
            'Src': 'H5',
            'Terminal-Src': 'H5'
        })
        self.api_src = 'H5'
        self.api_ver = "4.3.3-20240404095840"

    def get_city_list(self):
        """
        :return:
        """
        try:
            url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/home/pub/v3/citys'
            params = {
                'src': self.api_src,
                'ver': self.api_ver
            }
            response = self.http.get(url, params=params)
            data = response.json()
            city_list = []
            for item in data.get('data').get('allCities'):
                city_list.append({
                    'city_id': item['cities'][0]['cityId'],
                    'city_name': item['cities'][0]['cityName'],
                    'site_id': item['cities'][0]['siteId'],
                })
            return city_list
        except Exception as e:
            print(f"获取城市列表失败, {e.args}")
            return []

    def get_show_list(self, city_id):
        """
        获取即将开抢的演唱会列表
        :return:
        """
        try:
            url = 'https://m.piaoxingqiu.com/cyy_gatewayapi/home/pub/v3/floors'
            params = {
                'src': self.api_src,
                'ver': self.api_ver,
                'cityId': city_id
            }
            response = self.http.get(url, params=params)
            data = response.json()
            show_list = []
            for item in data['data']:
                for show in item['rooms'][0]['items']:
                    if 'latestSaleTime' in show:
                        show_list.append(show)
            return show_list
        except Exception as e:
            print(f'获取演出失败:{e.args}')

    def run(self):
        city_list = self.get_city_list()
        if not city_list:
            print("获取城市列表失败, 退出程序...")
            return

        all_show_list = []
        for city in city_list:
            print('正在获取{}即将开抢的演唱会列表...'.format(city['city_name']))
            show_list = self.get_show_list(city['city_id'])
            print('{},获取到{}个演唱会'.format(city['city_name'], len(show_list)))
            all_show_list.extend(show_list)
            time.sleep(2)

        show_list = []
        for item in all_show_list:
            # 计算三天后的日期时间对象
            three_days_later = datetime.datetime.now() + datetime.timedelta(days=3)

            # 将三天后的日期时间对象转换为毫秒时间戳
            three_days_later_timestamp = three_days_later.timestamp() * 1000

            if item.get('saleTime', None) and item['saleTime'] > three_days_later_timestamp:
                continue

            if item.get('saleTime', None):
                sale_time = datetime.datetime.fromtimestamp(item['saleTime'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            else:
                sale_time = item['latestSaleTime']
            show_list.append({
                'city_name': item['cityName'],
                'show_name': item['title'],
                'sale_time': sale_time,
                'id': item['id']
            })
        unique_dict_list = [dict(t) for t in {tuple(d.items()) for d in show_list}]
        msg = '### 近期开售的演出列表: \n'

        for item in unique_dict_list:
            msg += '- {}(id:{}), 开售时间:{}\n'.format(item['show_name'], item['id'], item['sale_time'])
        return msg


def server_jiang_notify(key, title, msg=''):
    """
        :param key:
        :param title:
        :param msg:
        :return:
        """
    try:
        url = f'https://sctapi.ftqq.com/{key}.send'
        data = {
            'title': title,
            'desp': msg,
        }
        response = requests.post(url, json=data)
        if response.json().get('code', -1) == 0:
            return True
        else:
            print("发送通知失败, {}".format(response.json()['message']))
    except Exception as e:
        print(f"发送通知失败:{e.args}")
    return False


def main():
    app = PxqShowMonitor()
    message = app.run()
    with open('README.md', 'r') as f:
        content = f.read()

    content = re.sub('<!-- SHOW_START -->([\s\S]*?)<!-- SHOW_END -->',
                     f'<!-- SHOW_START -->\n{message}\n<!-- SHOW_END -->', content)

    with open('README.md', 'w') as f:
        f.write(content)


if __name__ == '__main__':
    main()


