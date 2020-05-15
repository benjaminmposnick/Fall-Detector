# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import numpy as np
import sys
import asyncio
from six.moves import input
import threading
import json
from azure.iot.device.aio import IoTHubModuleClient


async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception(
                "The sample requires python 3.5.3+. Current version of Python: %s"
                % sys.version)
        print("IoT Hub Client for Python")

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()
        print("Module client connected")

        data_dir = "./simulator_data/"
        ex_num = 0
        ext = ".txt"

        while ex_num < 30:
            for file_name in os.listdir(data_dir):
                print("Receiving data from:", file_name, "\n\n")
                if ext not in file_name:
                    continue
                f = open(data_dir + file_name)
                for line in f:
                    samples = line.split(",")
                    samples[0] = samples[0].split("[ ")[1]  # remove "[ "
                    samples[-1] = samples[-1].split("]")[0]  # remove "]"

                    samples = np.asarray(list(map(float, samples)))
                    await module_client.send_message_to_output(
                        build_json(ex_num, list(samples.tolist())), "output1")
                    ex_num += 1

                    # to simulate collecting data in 1 sec intervals then analyzing
                    time.sleep(1)
                    if "fall" in file_name:
                        f.close()
                        break
                        # Just send one example for now from fall dataset, so as not to
                        # overwhelm email inbox with excessive falls (i.e. every second)
        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input()
                    if selection == "Q" or selection == "q":
                        break
                except:
                    time.sleep(10)

        # f = open("simulator_data/test_data_fall.txt")
        # print(f.readline())
        # output_object = json.dumps({"name": "test", "data": [[1, 2, 3]]})
        # output_message = json.dumps(output_object)
        # for _ in range(10):
        #     await module_client.send_message_to_output(output_message,
        #                                                "output1")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print("Unexpected error %s " % e)
        raise


class DataPoint():
    def __init__(self, name, data_matrix):
        self.name = name
        self.data_matrix = data_matrix


def build_json(ex_num, data):
    return json.dumps({"exampleNumber": ex_num, "data": data})


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())
