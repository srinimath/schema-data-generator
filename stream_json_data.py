from jsf import JSF
import sys
import time
import configparser
from azure.eventhub import EventHubProducerClient, EventData

def data_generator(json_schema, data_count):
    data_count_int = int(data_count)
    data_profile = JSF.from_json(json_schema)
    return str(data_profile.generate(data_count_int))

def stream_to_azure(config_params):

    

    i = 0
    loop_count_int = int(config_params['loop_count'])
    while(i < loop_count_int):
        data = data_generator(config_params['json_schema'], config_params['data_count'])

        connection_str = config_params['event_hub_conn_str']
        eventhub_name = config_params['event_hub_name']
        client = EventHubProducerClient.from_connection_string(connection_str, eventhub_name=eventhub_name)

        event_data_batch = client.create_batch()
        can_add = True
        while can_add:
            try:            
                event_data_batch.add(EventData(data))
            except ValueError:
                can_add = False  # EventDataBatch object reaches max_size.

        with client:
            client.send_batch(event_data_batch)
        print(data)
        time.sleep(int(config_params['wait_in_secs']))
        i = i + 1


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('stream_configurations.config')
    config_params = config['parameters']
    stream_to_azure(config_params)