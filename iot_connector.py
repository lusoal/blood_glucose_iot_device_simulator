from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
from datetime import datetime, timedelta
import csv


def initiate_client(client_id, iot_core_endpoint, ca_path, key_path, pem_path):
    myMQTTClient = AWSIoTMQTTClient(client_id)

    # Configure the MQTT Client
    myMQTTClient.configureEndpoint(iot_core_endpoint, 443)
    myMQTTClient.configureCredentials(ca_path, key_path, pem_path)
    myMQTTClient.configureOfflinePublishQueueing(
        -1
    )  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(10)  # 5 sec

    return myMQTTClient


def publish_new_message(client, topic_name, message):
    try:
        client.connect()
    except Exception as e:
        raise e
    try:
        json_message = json.dumps(message)
        client.publish(topic_name, json_message, 0)
        print(f"Message published in topic {topic_name}")
        client.disconnect()
    except Exception as e:
        print(f"[Error] {e}")
        raise Exception("Not able to parser message as Json")


def timeDiff(time1, time2):
    timeA = datetime.strptime(time1, "%H:%M")
    timeB = datetime.strptime(time2, "%H:%M")
    newTime = timeA - timeB
    diff_minutes = newTime.seconds / 60

    if diff_minutes < 10:
        print(f"[INFO] Enviar o dataset a partir desta hora {time2}")
        return True
    return False


def load_csv_to_dict(csv_path, user_id):
    my_list_dict = []
    with open(csv_path, mode="r") as infile:
        reader = csv.reader(infile)
        now = datetime.now()
        count = 0
        correct_list = []
        reader = list(reader)

        # Ajustando a partir de qual horario vou coletar o CSV
        for rows in reader:
            timestamp = datetime.strptime(rows[0], "%Y-%m-%d %H:%M:%S")
            difference = timeDiff(
                f"{now.hour}:{now.minute}", f"{timestamp.hour}:{timestamp.minute}"
            )
            if not difference:
                count += 1
                continue
            else:
                correct_list = reader[count:]
            break

        # Montando a lista de dicionarios
        for rows in correct_list:
            my_dict = {}
            my_dict["user_id"] = user_id  # user_id == device_id
            my_dict["glicose"] = float(rows[1])  # Convertendo para float
            my_dict["insulina"] = 0
            # TODO: falar da possibilidade de agregar
            # mais informacoes como por exemplo, insulina e carboidrato
            my_dict["carbo"] = 0
            my_dict["timestamp"] = rows[0]
            my_list_dict.append(my_dict)

    return my_list_dict


def transform_in_current_data(list_dict_csv, time_ago=3, increment=300):
    current_data_list = []
    now = datetime.now()
    time_ago = time_ago * 86400

    days_ago = now - timedelta(
        seconds=time_ago
    )  # TODO: Deixar escolher quantidade de dias para simular
    now_incremented = days_ago

    # Criando forecast de três dias atras
    list_dict_csv[0]["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")
    # list_dict_csv[0]['timestamp'] = now.isoformat()

    current_data_list.append(list_dict_csv[0])
    for line in list_dict_csv[1:]:
        now_incremented = now_incremented + timedelta(seconds=increment)
        line["timestamp"] = now_incremented.strftime("%Y-%m-%d %H:%M:%S")
        # line["timestamp"] = now_incremented.isoformat()
        current_data_list.append(line)

    return current_data_list


def publish_to_iot_core_parsed(device_id, item):
    # TODO: Definir como variavel de ambiente
    iot_core_endpoint = "a39nx2epzfsfmt-ats.iot.us-east-1.amazonaws.com"
    ca_path = "certificates/ca.crt"
    key_path = "certificates/ad2bf044c8-private.pem.key"
    cert_path = "certificates/ad2bf044c8-certificate.pem.crt"

    topic_name = f"blood_analysis/{device_id}"

    mqtt_client = initiate_client(
        device_id, iot_core_endpoint, ca_path, key_path, cert_path
    )

    print(f"[INFO] sending {item} on topic {topic_name}")
    try:
        publish_new_message(mqtt_client, topic_name, item)
    except Exception as e:
        print(f"[Error] {e}")
        pass

    # loaded_data = load_csv_to_dict("data/glucose_csv_final.csv", device_id)
    # loaded_data_current = transform_in_current_data(loaded_data)

    # for item in csv_current_loaded:
    #     try:
    #         # TODO: Substituir deviceid por device enviado a partir do frontend
    #         timestamp = item['timestamp']
    #         timestamp_date_object = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    #         now = datetime.now()
    #         test = now - timestamp_date_object

    #         if int(test.days) < 0:
    #             break

    #         print(f"[INFO] sending {item} of device {device_id} to topic {topic_name}")
    #         # publish_new_message(mqtt_client, topic_name, item)
    #         # time.sleep(2)
    #     except Exception as e:
    #         print(e)
    #         csv_current_loaded.append(item)
    #         continue
