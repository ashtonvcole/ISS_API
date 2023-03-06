# ISS Orbit Tracking API

This project creates a simple, locally-hosted Flask API to process HTTP requests for trajectory data for the International Space Station. It then accesses an XML-format Orbital Ephemeris Message from NASA, which it filters and processes to satisfy the query and returns to the user in text or JSON format. More information on the data set can be found [on the NASA website](https://spotthestation.nasa.gov/trajectory_data.cfm).

This assignment is important, because it empowers users to easily access and filter through a large data set. Instead of receiving a complicated XML file of the whole data set, a user can request only what they need, and receive it in JSON.

## Running the Project

This project allows users to either run the Python script on their own machine or within a Docker cotainer. Docker containers are useful because they neatly package a program with all of its dependencies, and create an isolated, consistent runtime environment across machines.

Note that the app retrieves data when it is initialized. To modify or update the data set, browse the [endpoints](#endpoints).

### Running with Python

This project requires Python 3 to run. It also requires a stable internet connection and the modules `flask`, `requests`, `xmltodict`, and `geopy`. The server can be started by changing the permissions of [`iss_tracker.py`](iss_tracker.py) to make it executable, or running it with the `python3` command. Alternatively, it can be run with the command `flask --app iss_tracker --debug run`. All put the server in debug mode. From another terminal window, you may use the `curl` command to make HTTP requests.

### Running With Docker

With Docker containerization, the program only needs Docker and a stable internet connection. The Dockerfile installs all dependencies for you! First, the image needs to be pulled from [Docker Hub](https://hub.docker.com/repository/docker/ashtonvcole/iss_tracker/general).

```bash
docker pull ashtonvcole/iss_tracker:hw05
```

Alternatively, the contents of this folder can be downloaded to your machine, and you can build the Docker image yourself. In the directory with `iss_tracker.py` and `Dockerfile`, run the following command.

```bash
docker build -t <your_image_name> .
```

Once you have an image, you can run it. This can be performed with Docker or docker-compose.

With Docker, starting the container automatically initializes the program, but you must bind the container's port to your machine's as follows. In the example command, `-it` binds the program's input and output to your own terminal, `--rm` removes the container after you have finished running it, and `-p 5000:5000` binds port 5000 on your machine to port 5000 on the container.

```bash
docker run -it --rm -p 5000:5000 ashtonvcole/iss_tracker:hw05
```

The docker-compose option simplifies the process by automatically configuring some of these startup commands. You may simply pull the image, navigate to the directory with the [`docker-compose.yml`](docker-compose.yml) file, and run the following command to start up a container.

```bash
docker-compose up
```

## Project Structure

The project consists of two files.

- `Dockerfile` [About](#dockerfile) [File](Dockerfile)
- `docker-compose.yml` [About](#docker-composeyml) [File](docker-compose.yml)
- `iss_tracker.py` [About](#iss_trackerpy) [File](iss_tracker.py)

### [`Dockerfile`](Dockerfile)

This script is used to build a Docker image, which can excecute the program within a container. See [Running with Docker](#running-with-docker).

### [`docker-compose.yml`](docker-compose.yml)

This file is used to build a Docker container, automating some configuration steps. See [Running with Docker](#running-with-docker).

### [`iss_tracker.py`](iss_tracker.py)

This script processes all HTTP requests to the API. In addition to code that initializes the server, it contains several functions which execute and return data for a certain endpoint. 

## Endpoints

The following endpoints are available to the user. Note that all endpoints, given irregular inputs, will return a string message with a 404 status code.

- `/`
- [`/epochs`](#epochs)
- [`/epochs/<epoch>`](#epochsepoch)
- [`/epochs/<epoch>/speed`](#epochsepochspeed)
- [`/epochs/<epoch>/location`](#epochsepochlocation)
- [`/now`](#now)
- [`/delete-data`](#delete-data)
- [`/post-data`](#post-data)
- [`/help`](#help)
- [`/comment`](#comment)
- [`/header`](#header)
- [`/metadata`](#metadata)

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
  "value": 7.658223206788738,
  "units": "km/s"
}
```

As expected, the result is the square root of the sum of the squares of the velocity components.

### `/epochs/<epoch>/location`

This returns a variety of location parameters including the latitude, longitude, and altitude for a given epoch. It also shows the nearest ground location below the ISS at that time, or `null` if the point is over the ocean or otherwise remote. Epochs are in the form `YYYY-DDDTHH:MM:SS.000Z`, which means that `<epoch>` needs to be formatted with character codes as `YYYY-DDDTHH%3AMM%3ASS%2E000Z`. If the data set is empty or the inputs are poorly formed, it will return a string message with a 404 status code.

```bash
curl http://localhost:5000/epochs/2023-077T15%3A47%3A35%2E995Z/location
```

```json
{
  "closest_epoch": "2023-077T15:47:35.995Z",
  "location": {
    "altitude": {
      "units": "km",
      "value": 428.6137193341565
    },
    "geo": {
      "address": {
        "ISO3166-2-lvl4": "AO-BGU",
        "country": "Angola",
        "country_code": "ao",
        "state": "Benguela Province"
      },
      "boundingbox": [
        "-13.874445",
        "-11.7589169",
        "12.3159609",
        "15.1108341"
      ],
      "display_name": "Benguela Province, Angola",
      "lat": "-12.9104657",
      "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
      "lon": "14.0356608",
      "osm_id": 1802540,
      "osm_type": "relation",
      "place_id": 298335923
    },
    "latitude": -13.479282638990789,
    "longitude": 13.126560404682472
  },
  "seconds_from_now": 0,
  "speed": {
    "units": "km/s",
    "value": 7.6577354899224375
  }
}
```

### `/now`

This provides the same [location information](#epochsepochlocation) as before, for the epoch closest to the present. It also informs the user of the time difference between the current time and epoch, in seconds. If the data set is empty, it will return a string message with a 404 status code.

```bash
curl http://localhost:5000/now
```

```json
{
  "closest_epoch": "2023-065T22:59:30.000Z",
  "location": {
    "altitude": {
      "units": "km",
      "value": 430.322553722729
    },
    "geo": null,
    "latitude": -15.297069227120538,
    "longitude": -193.6978998196031
  },
  "seconds_from_now": -8.718001127243042,
  "speed": {
    "units": "km/s",
    "value": 7.6552459153446755
  }
}
```

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
status.

Note that epochs are in the form
YYYY-DDDTHH:MM:SS.000Z, or in URL-friendly form
YYYY-DDDTHH%3AMM%3ASS%2E000Z

        / GET Return the entire data set in JSON form.
        /epochs GET Return a list of all epochs in JSON form.
                int:limit The maximum number of epochs to return.
                int:offset What epoch to start from, zero-indexed
        /epochs/<epoch> GET Return the state vector for
                an epoch in JSON form. Returns a string error
                message with a 404 status if no such record.
        /epochs/<epoch>/speed GET Return the instantaneous
                speed for an epoch in JSON form. Returns a string
                error message with a 404 status if no such record.
        /epochs/<epoch>/location GET Return a dictionary of
                the latitude, longitude, altitude, and geoposition
                for an epoch in JSON form. Returns a string error
                message with a 404 status if no such record.
        /now GET Return a dictionary of the latitude,
                longitude, altitude, and geoposition for the closest
                epoch to present in JSON form. It also indicates
                how far away in time the closest epoch is.
        /delete-data DETETE Clear all data in the instance.
        /post-data POST Update and overwrite all data.
        /comment GET Return comment list from data.
        /header GET Return header dictionary from data.
        /metadata GET Return metadata dictionary from data.
```

### `/comment`

This provides the comments added to the data file in JSON form. This includes information about the conventions used to represent the orbit and upcoming trajectory events. If the data set is empty, it will return a string message with a 404 status code.

```bash
curl localhost:5000/comment
```

```json
[
  "Units are in kg and m^2",
  "MASS=473413.00",
  "DRAG_AREA=1618.40",
  "DRAG_COEFF=2.20",
  "SOLAR_RAD_AREA=0.00",
  "SOLAR_RAD_COEFF=0.00",
  "Orbits start at the ascending node epoch",
  "ISS first asc. node: EPOCH = 2023-03-03T16:45:01.089 $ ORBIT = 2542 $ LAN(DEG) = 78.61627",
  "ISS last asc. node : EPOCH = 2023-03-18T14:19:09.505 $ ORBIT = 2773 $ LAN(DEG) = 26.64425",
  "Begin sequence of events",
  "TRAJECTORY EVENT SUMMARY:",
  null,
  "|       EVENT        |       TIG        | ORB |   DV    |   HA    |   HP    |",
  "|                    |       GMT        |     |   M/S   |   KM    |   KM    |",
  "|                    |                  |     |  (F/S)  |  (NM)   |  (NM)   |",
  "=============================================================================",
  "GMT 067 ISS Reboost   067:20:02:00.000             1.0     427.0     407.3",
  "(3.3)   (230.6)   (219.9)",
  null,
  "Crew05 Undock         068:08:00:00.000             0.0     427.0     410.8",
  "(0.0)   (230.6)   (221.8)",
  null,
  "SpX27 Launch          074:00:30:00.000             0.0     426.7     409.9",
  "(0.0)   (230.4)   (221.3)",
  null,
  "SpX27 Docking         075:12:00:00.000             0.0     426.7     409.8",
  "(0.0)   (230.4)   (221.3)",
  null,
  "=============================================================================",
  "End sequence of events"
]
```

### `/header`

This provides the header added to the file in JSON form. This includes information about the creation of the data file. If the data set is empty, it will return a string message with a 404 status code.

```bash
curl localhost:5000/header
```

```json
{
  "CREATION_DATE": "2023-063T04:34:04.606Z",
  "ORIGINATOR": "JSC"
}
```

### `/metadata`

This provides the metadata added to the file in JSON form. This includes identifiers for the orbital center and orbiting object, time and spatial references, and start and stop times. If the data set is empty, it will return a string message with a 404 status code.

```bash
curl localhost:5000/metadata
```

```json
{
  "CENTER_NAME": "EARTH",
  "OBJECT_ID": "1998-067-A",
  "OBJECT_NAME": "ISS",
  "REF_FRAME": "EME2000",
  "START_TIME": "2023-062T15:47:35.995Z",
  "STOP_TIME": "2023-077T15:47:35.995Z",
  "TIME_SYSTEM": "UTC"
}
```
