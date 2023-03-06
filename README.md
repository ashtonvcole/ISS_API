# ISS Orbit API, Now with Docker!

This project creates a simple, locally-hosted Flask API to process HTTP requests for trajectory data for the International Space Station. It then accesses an XML-format Orbital Ephemeris Message from NASA, which it filters and processes to satisfy the query and returns to the user in text or JSON format. More information on the data set can be found [on the NASA website](https://spotthestation.nasa.gov/trajectory_data.cfm).

This assignment is important, because it demonstrates how Python, a relatively simple programming language, can be applied to create a web API capable of acessing and processing large data sets. It also has value from a user perspective, since instead of receiving a complicated XML file of the whole data set, a user can request only what they need, and receive it in JSON.

## Running the Project

This project now allows users to either run the Python script on their own machine or within a Docker cotainer. Docker containers are useful because they neatly package a program with all of its dependencies, and create an isolated, consistent runtime environment across machines.

Note that the app retrieves data when it is initialized. To modify or update the data set, browse the [endpoints](#endpoints).

### Running with Python

This project requires Python 3 to run. It also requires a stable internet connection and the modules `requests` and `xmltodict`. The server can be started by changing the permissions of [`iss_tracker.py`](iss_tracker.py) to make it executable, or running it with the `python3` command. Alternatively, it can be run with the command `flask --app iss_tracker --debug run`. All put the server in debug mode. From another terminal window, you may usse the `curl` command to make HTTP requests.

### Running With Docker

With Docker containerization, the program only needs Docker and a stable internet connection. The Dockerfile installs all dependencies for you! First, the image needs to be pulled from [Docker Hub](https://hub.docker.com/repository/docker/ashtonvcole/iss_tracker/general).

```bash
docker pull ashtonvcole/iss_tracker:hw05
```

Alternatively, the contents of this folder can be downloaded to your machine, and you can build the Docker image yourself. In the directory with `iss_tracker.py` and `Dockerfile`, run the following command.

```bash
docker build -t <your_image_name> .
```

Once you have an image, you can run it. Starting the container automatically initializes the program, but you must bind the container's port to your machine's as follows. In the example command, `-it` binds the program's input and output to your own terminal, `--rm` removes the container after you have finished running it, and `-p 5000:5000` binds port 5000 on your machine to port 5000 on the container.

```bash
docker run -it --rm -p 5000:5000 ashtonvcole/iss_tracker:hw05
```

## Project Structure

The project consists of two files.

- `Dockerfile` [About](#Dockerfile) [File](Dockerfile)
- `iss_tracker.py` [About](#iss_trackerpy) [File](iss_tracker.py)

### [`Dockerfile`](Dockerfile)

This script is used to build a Docker image, which can excecute the program within a container. See [Running with Docker](#running-with-docker).

### [`iss_tracker.py`](iss_tracker.py)

This script processes all HTTP requests to the API. In addition to code that initializes the server, it contains several functions which execute and return data for a certain endpoint.

## Endpoints

The following endpoints are available to the user. Note that all endpoints, given irregular inputs, will return a string message with a 404 status code.

- `/`
- [`/epochs`](#epochs)
- [`/epochs/<epoch>`](#epochsepoch)
- [`/epochs/<epoch>/speed`](epochsepochspeed)
- [`/delete-data`](#delete-data)
- [`/post-data`](#post-data)
- [`/help`](#help)

### `/`

This returns the entire data set in JSON format. Each state vector is an item in a list associated with the nested dictionary entries `"ndm"`, `"oem"`, `"body"`, `"segment"`, `"data"`, and `"stateVector"`. If the data set is empty, it will return a string message with a 404 status code.

```bash
curl localhost:5000/
```

```json
{
  "ndm": {
    "oem": {
      "@id": "CCSDS_OEM_VERS",
      "@version": "2.0",
      "body": {
        "segment": {
          "data": {
            "stateVector": [
              {
                "EPOCH": "2023-048T12:00:00.000Z",
                "X": {
                  "#text": "-5097.51711371908",
                  "@units": "km"
                },
                "X_DOT": {
                  "#text": "-4.5815461024513304",
                  "@units": "km/s"
                },
                "Y": {
                  "#text": "1610.3574036042901",
                  "@units": "km"
                },
                "Y_DOT": {
                  "#text": "-4.8951801207083303",
                  "@units": "km/s"
                },
                "Z": {
                  "#text": "-4194.4848049601396",
                  "@units": "km"
                },
                "Z_DOT": {
                  "#text": "3.70067961081915",
                  "@units": "km/s"
                }
              },
              ...
            ]
          },
          "metadata": {
            "CENTER_NAME": "EARTH",
            "OBJECT_ID": "1998-067-A",
            "OBJECT_NAME": "ISS",
            "REF_FRAME": "EME2000",
            "START_TIME": "2023-048T12:00:00.000Z",
            "STOP_TIME": "2023-063T12:00:00.000Z",
            "TIME_SYSTEM": "UTC"
          }
        }
      },
      "header": {
        "CREATION_DATE": "2023-049T01:38:49.191Z",
        "ORIGINATOR": "JSC"
      }
    }
  }
}
```

### `/epochs`

This returns a list of all epochs in JSON format. This is the time associated with a data point. They are in the form `YYYY-DDDTHH:MM:SS.000Z`. Two optional integer parameters are available, with `offset` defining how many entries the result is offset from the first, and `limit` setting a maximum for the number of epochs returned. If the data set is empty or the inputs are poorly formed, it will return a string message with a 404 status code.

```bash
curl 'localhost:5000/epochs?offset=0&limit=5'
```

```json
[
  "2023-048T12:00:00.000Z",
  "2023-048T12:04:00.000Z",
  "2023-048T12:08:00.000Z",
  "2023-048T12:12:00.000Z",
  "2023-048T12:16:00.000Z"
]
```

### `/epochs/<epoch>`

This returns the state vector associated with a given epoch in JSON format. This includes the epoch, position, and velocity components. Epochs are in the form `YYYY-DDDTHH:MM:SS.000Z`, which means that `<epoch>` needs to be formatted with character codes as `YYYY-DDDTHH%3AMM%3ASS%2E000Z`. If the data set is empty or the inputs are poorly formed, it will return a string message with a 404 status code.

```bash
curl localhost:5000/epochs/2023-048T12%3A00%3A00%2E000Z
```

```json
{
  "EPOCH": "2023-048T12:00:00.000Z",
  "X": {
    "#text": "-5097.51711371908",
    "@units": "km"
  },
  "X_DOT": {
    "#text": "-4.5815461024513304",
    "@units": "km/s"
  },
  "Y": {
    "#text": "1610.3574036042901",
    "@units": "km"
  },
  "Y_DOT": {
    "#text": "-4.8951801207083303",
    "@units": "km/s"
  },
  "Z": {
    "#text": "-4194.4848049601396",
    "@units": "km"
  },
  "Z_DOT": {
    "#text": "3.70067961081915",
    "@units": "km/s"
  }
}
```

### `/epochs/<epoch>/speed`

This returns the speed, i.e. 2-norm, of the velocity components. It is returned in JSON format, along with the units associated with `"X_DOT"`. Epochs are in the form `YYYY-DDDTHH:MM:SS.000Z`, which means that `<epoch>` needs to be formatted with character codes as `YYYY-DDDTHH%3AMM%3ASS%2E000Z`. If the data set is empty or the inputs are poorly formed, it will return a string message with a 404 status code.

```bash
curl localhost:5000/epochs/2023-048T12%3A00%3A00%2E000Z/speed
```

```json
{
  "speed": 7.658223206788738,
  "units": "km/s"
}
```

As expected, the result is the square root of the sum of the squares of the velocity components.

### `/delete-data`

This clears all data from the data set of the instance. It uses the HTTP `DELETE` method.

```bash
curl localhost:5000/delete-data -X DELETE
```

```
Data deleted from instance
```

### `/post-data`

This overwrites existing data in the instance with the most up-to-date information available through the [NASA website](https://spotthestation.nasa.gov/trajectory_data.cfm). It uses the HTTP `POST` method.

```bash
curl localhost:5000/post-data -X POST
```

```
Data refreshed
```

### `/help`

This provides the same catalog of API endpoints with brief desctiptions.

```bash
curl localhost:5000/help
```

```
These are the endpoints of the iss_tracker API.

Note that if the data is empty, all GET
messages will return a string message with a 404
status

  / GET Return the entire data set in JSON form.
  /epochs GET Return a list of all epochs in JSON form.
    int:limit The maximum number of epochs to return.
    int:offset What epoch to start from, zero-indexed
  /epochs/<int:epoch> GET Return the state vector for
    an epoch in JSON form. Returns a string error
    message with a 404 status if no such record.
  /epochs/<int:epoch>/speed GET Return the instantaneous
    speed for an epoch in JSON form. Returns a string
    error message with a 404 status if no such record.
  /delete-data DETETE Clear all data in the instance.
  /post-data POST Update and overwrite all data.
```
