# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import requests
from collections import deque
import numpy as np
import sys
import asyncio
import json
from six.moves import input
import threading
from sensor_simulator import simulate_input
from azure.iot.device.aio import IoTHubModuleClient
import csv


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

        addr = "abdevelopertest@gmail.com"
        home_id = os.environ['HOME_ID']  # This is also in an env variable
        print("Home ID: " + home_id)
        function_baseurl = "https://falldetectoralertservice.azurewebsites.net/api/httpresponder?code=NZSyiywm5hBcFLhx4AaSalEdHGsgPGeYpqbkmhnMsWOpmlHREs7ZhA==&addr="
        function_baseurl += addr + "&homeId=" + home_id
        with open('scalability_test.csv', mode='x') as time_csv:
            time_writer = csv.writer(time_csv, delimiter=',')
            simulate_input(function_baseurl, 10, time_writer)

        # await module_client.send_message("\{message:\"Output on home " +
        #                                  str(home_id) + "finished\"\}")

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print("Unexpected error %s " % e)
        raise


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

#     # If using Python 3.7 or above, you can use following code instead:
#     # asyncio.run(main())
