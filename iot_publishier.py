import iot_connector
from utils import (
    write_tosend_sended_file,
    get_values_already_sended,
    validate_date_to_send,
)
from flask import Flask, render_template, redirect, url_for, session, request
import os

app = Flask(__name__)
app.secret_key = "eipohgoo4rai0uf5ie1oshahmaeF"

# Application routes
@app.route("/", methods=["GET"])
def index():
    try:
        os.remove("mutable_data/tmp_file.txt")
        os.remove("mutable_data/already_sended.txt")
    except Exception as e:
        print(f"[Error] o arquivo nao existe {e}")
        pass
    session["count"] = 0
    return render_template("index.html")


@app.route("/parsed_csv_load_data", methods=["GET", "POST"])
def parsed_csv_load_data():
    device_id = request.form.get("device_id", "")
    time_to_generate = int(
        request.form.get("time_to_generate", "")
    )  # Dias atras para simular os dados

    csv_dict_loaded = iot_connector.load_csv_to_dict(
        "data/glucose_second.csv", device_id
    )
    csv_dict_loaded_current = iot_connector.transform_in_current_data(
        csv_dict_loaded, time_to_generate
    )

    with open("mutable_data/tmp_file.txt", "w") as f:
        f.write(str(csv_dict_loaded_current))

    return redirect(url_for("publish_to_iot_core"))


@app.route("/publish_to_iot_core", methods=["GET"])
def publish_to_iot_core():
    data_to_send_path = "mutable_data/tmp_file.txt"
    data_already_sended_path = "mutable_data/already_sended.txt"

    session["count"] += 1

    send_value = write_tosend_sended_file(data_to_send_path, data_already_sended_path)

    device_id = send_value["user_id"]
    timestamp = send_value["timestamp"]

    if not validate_date_to_send(timestamp):
        return "Dados carregados com sucesso"

    # Converter para tipo de dado que o Athena entende como Timestamp

    iot_connector.publish_to_iot_core_parsed(device_id, send_value)

    already_sended = get_values_already_sended(data_already_sended_path)

    return render_template(
        "show_sended_iot_core.html",
        already_sended=already_sended,
        device_id=device_id,
        quantidade_enviada=session["count"],
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
