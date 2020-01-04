import json
import requests
import main.import_django_settings
from django.conf import settings
import time

control_seconds = 60
list_total = 20
send_id_list = []
send_id_to_time = {}

def send_message(msg, type = 0):
    """

    :param msg:
    :param type: 0其他业务报警，1是ai训练进程，2是ai守护进程，3是app守护进程
    :return:
    """
    send_id = control_send_frequence()

    access_token = '847c216695a0a56489956201584f3198a7b48abb91f6f47b3c67511b28dd3e9c'
    if type == 1:
        alert_name = 'ai训练进程报警'
    elif type == 2:
        alert_name = 'ai守护程报警'
    elif type == 3:
        alert_name = 'app守护进程报警'
    else:
        alert_name = '其他报警'

    url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(access_token)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    msg_json = {"msgtype": "text",
                "text": {
                    "content": "{}：{}".format(alert_name, msg)
                }
                }
    json_info = json.dumps(msg_json)

    data = bytes(json_info, 'utf8')
    resp = requests.post(url=url, data=data, headers=headers)
    print('业务报警发送结果：{},{}'.format(resp, msg))

    # 更新最后信息的发送时间
    send_id_to_time[send_id] = time.time()


def control_send_frequence():
    if len(send_id_list) == list_total:
        # 判断发送队列数据是否要sleep
        cur_time = time.time()
        last_send_id = None
        for send_id in send_id_list:
            if cur_time - send_id_to_time[send_id] < control_seconds:
                last_send_id = send_id
            else:
                break

        if last_send_id is not None:
            sleep_time = control_seconds - int(cur_time - send_id_to_time[last_send_id]) + 1
            print('发送过于频繁，sleep {}秒'.format(sleep_time))
            time.sleep(sleep_time)

        # 清理列表
        cur_time = time.time()
        remove_list = []
        for send_id in send_id_list:
            if cur_time - send_id_to_time[send_id] > control_seconds:
                remove_list.append(send_id)
            else:
                break

        for send_id in remove_list:
            send_id_list.remove(send_id)
            send_id_to_time.pop(send_id)

    # 增加发送队列数据
    if len(send_id_list) == 0:
        send_id = 0
    else:
        send_id = send_id_list[-1] + 1
    send_id_list.append(send_id)
    return send_id


if __name__ == "__main__":
    for i in range(50):
        send_message('测试信息{}！'.format(i))
