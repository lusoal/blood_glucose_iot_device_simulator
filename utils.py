import ast
from datetime import datetime
import os

# import dateutil.parser


def write_tosend_sended_file(path_to_send, path_sended):
    loaded_current = None

    with open(path_to_send, "r") as file:
        loaded_current = ast.literal_eval(
            file.read()
        )  # Pegando dados para enviar a partir do arquivo

    print(f"[INFO] Faltam {len(loaded_current)} para serem enviados")
    send_value = loaded_current.pop(0)  # Esse sera o valor para enviar

    with open(path_to_send, "w") as f:  # Rescrevendo dados que já foram enviados
        f.write(str(loaded_current))

    with open(path_sended, "a+") as file:
        file.write(f"{str(send_value)},")  # Dados ja enviados para exibir no front

    return send_value


def get_values_already_sended(path_sended):
    already_sended = None

    with open(path_sended, "r") as file:
        already_sended = ast.literal_eval(file.read())  # Pegando dados já enviados

    if len(already_sended) > 10:
        os.remove(path_sended)
        print("[INFO] Zerar o arquivo com dados ja enviados")  # Zerando lista

    return already_sended


def validate_date_to_send(timestamp):
    timestamp_date_object = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    # timestamp_date_object = dateutil.parser.parse(timestamp)
    now = datetime.now()
    comparasion = now - timestamp_date_object

    print(f"[INFO] dados de {comparasion.days} atrás sendo enviados")

    if int(comparasion.days) < 0:
        return False

    return True
