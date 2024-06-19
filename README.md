# sky-interview-task

## Run Locally

Clone the project with https

```bash
  git clone https://github.com/Albi-Miraka/sky-interview-task.git
```

Clone the project with ssh

```bash
  git clone git@github.com:Albi-Miraka/sky-interview-task.git
```

Go to the project directory

```bash
  cd sky-interview-task
```

In order to run the python script is necessary to install all modules that are specified into "requirements.txt"

```bash
  pip install -r requirements.txt
```
If you are on windows and receive an error that don't recognize the pip command than use

```bash
  py -m pip install -r requirements.txt
```

Run python script

```bash
  py -m src.main.main 
```

### Environment Variables

There are 3 variables that can be changed with CLI

`NUMBER_OF_ITERATIONS -> number of calls to do to the server before going in error [DEFAULT=3]`

`NUMBER_OF_ITERATIONS = 3 -> sometimes will throw an error`
`NUMBER_OF_ITERATIONS = 5 -> almost every time the execution will succed`

`PRINT_FILTER_BY_DEVICE -> print the names of TV shows/Movie titles filtered by device [DEFAULT=False]`

`PRINT_FILTER_BY_DEVICE_AND_ACTIVE -> print the names of TV shows/Movie titles filtered by device and with active rights [DEFAULT=False]`

example:
```bash
  py -m src.main.main NUMBER_OF_ITERATIONS=5 PRINT_FILTER_BY_DEVICE=True PRINT_FILTER_BY_DEVICE_AND_ACTIVE=True
```

## Running Tests

To run tests, from the root directory, run the following command

```bash
  py -m src\test\ResultTest.py
```

## Assumptions

From data retrieve by calling the endpoints: 
- https://ko3vcqvszf.execute-api.eu-west-1.amazonaws.com/vq
- https://ko3vcqvszf.execute-api.eu-west-1.amazonaws.com/tq

- 1 Assumption: content_id is a required attribute, because can identify both dataset
- 2 Assumption: "terms" MUST be an array of only one element and with "startDateTime" and "endDateTime" required field in order to check if a term is active or not

```json
  https://ko3vcqvszf.execute-api.eu-west-1.amazonaws.com/vq

    {
    "results": [
        {
            "serviceKey": 1,
            "contentId": "sky-test-id-1",
            "accessChannel": "itv3",
            "localizableInformation": [
                {
                    "locale": "en-GB",
                    "language": "eng",
                    "titleNameMedium": "Agatha Christie's Marple",
                    "episodeName": "The Secret of Chimneys",
                    "episodeNumber": 2,
                    "seasonNumber": 5,
                    "credits": {
                        "actor": [
                            {
                                "fullName": "Julia McKenzie"
                            },
                            {
                                "fullName": "Ian Weichardt"
                            },
                            {
                                "fullName": "Laura O'Toole"
                            }
                        ]
                    }
                }
            ],
            "rights": {
                "channel": "itv3.itv.com",
                "terms": [
                    {
                        "startDateTime": "2024-05-31T16:48:47.000Z",
                        "endDateTime": "2024-10-30T22:59:00.000Z",
                        "territory": "GB",
                        "devices": [
                            {
                                "devicePlatform": "APPLETV",
                                "deviceType": "IPSETTOPBOX",
                                "provider": "SKY"
                            },
                            {
                                "devicePlatform": "SAMSUNG",
                                "deviceType": "TV",
                                "provider": "SKY"
                            },
                            {
                                "devicePlatform": "LG",
                                "deviceType": "TV",
                                "provider": "SKY"
                            },
                            {
                                "devicePlatform": "ANDROID",
                                "deviceType": "MOBILE",
                                "provider": "SKY"
                            },
                            {
                                "devicePlatform": "IOS",
                                "deviceType": "MOBILE",
                                "provider": "SKY"
                            }
                        ]
                    }
                ]
            }
        }
    ]
}
```

```json
https://ko3vcqvszf.execute-api.eu-west-1.amazonaws.com/tq
{
    "results": [
        {
            "contentId": "sky-test-id-1",
            "accessChannel": "itv3",
            "assets": [
                {
                    "endpoints": [
                        {
                            "origin": "level3",
                            "path": "/skyplayer/level3/sky-test-id-1/sd/Manifest"
                        }
                    ],
                    "videoFormat": "SD"
                },
                {
                    "endpoints": [
                        {
                            "origin": "akamai",
                            "path": "/skyplayer/akamai/sky-test-id-1/hd/Manifest"
                        }
                    ],
                    "videoFormat": "HD"
                },
                {
                    "endpoints": [
                        {
                            "origin": "limelight",
                            "path": "/skyplayer/limelight/sky-test-id-1/sd/Manifest"
                        }
                    ],
                    "videoFormat": "SD"
                },
                {
                    "endpoints": [
                        {
                            "origin": "level3",
                            "path": "/skyplayer/level3/sky-test-id-1/hd/Manifest"
                        }
                    ],
                    "videoFormat": "HD"
                }
            ]
        }
    ]
}
```