# Halotone2mqtt
I created this Docker container in order to poll the Creality Halot One 3D resin printer and sent this data to a MQTT topic. You are able to use this data in Home Assistant to have an actual state of the device while printing. Right now the only solution is to use Creality their Cloud service & app.

# Credits
Thanks to @danielkucera for his work in figuring out the authentication used for the Halot One printer websocket.
https://github.com/danielkucera/creality-remote-control

To test your printer before using this container, try https://halot.gh.danman.eu/. This will let you know if the set password & wifi connection are working.

# Requirements
## Printer setup - Creality Halot One
On the printer itself, you have to join it to your Wifi network. After that, set a password in order to authenticate to your printer.

## MQTT setup
### Home Assistant MQTT setup
You have to setup the MQTT integration (with Mosquitto) and make it listen to your newly created topic. This works after you have run the container for the first time.

see: https://www.home-assistant.io/integrations/mqtt

### Topic
A topic is automatically generated when pushing data this container to your MQTT instance.
The given mqtt_topic name will be generated when not existing on the MQTT broker.

# Running the container
## Clone
Clone this repository to start building
```Shell
git clone https://github.com/sjanssen15/halotone2mqtt.git
cd halotone2mqtt
```

## Build image
Build the Docker image for your system.
```Shell
docker build -t halotone2mqtt:latest build/.
```

## Run docker-compose
Edit the docker-compose.yml with your own settings:
| **Env** |  |
|--|--|
| printerip | Your printer IP. You are unable to set a static IP on the printer. Try to make a DHCP static lease in order to have a static IP. |
| printerpass | Password set on the printer itself |
| mqtt_topic | A topic name in the format creality/halot (example) |
| mqtt_user | MQTT user you configured |
| mqtt_password | MQTT password |
| mqtt_ip | IP of your MQTT server |
| mqtt_port | Port of your MQTT (default 1883) |

Start the container with docker compose
```Shell
docker-compose up -d
```

View the logs
```Shell
docker logs -f halotone2mqtt-container
```

# Setting up Home Assistant
## MQTT data
You can use for instance **MQTT Explorer** to discover your topics and find the JSON data. Example data:
```json
{
  "bottomExposureNum": "0",
  "curSliceLayer": "0",
  "delayLight": "0",
  "eleSpeed": "0",
  "filename": "",
  "initExposure": "0",
  "layerThickness": "0",
  "printExposure": "0",
  "printHeight": "0",
  "printRemainTime": "0",
  "printStatus": "Ready to print",
  "resin": "0",
  "sliceLayerCount": "0"
}
```

## Home Assistant sensor
! This is a work in progress !
I use the following to get the MQTT data and parse it as sensors.

Edit your configuration.yaml and add a MQTT sensor:
```Yaml
mqtt:
  sensor:
    #### Halot One 3D printer
    - name: Halot One printstatus
      value_template: '{{ value_json.printStatus }}'
      state_topic: creality/halotone
      icon: mdi:printer-3d

    - name: Halot One filename
      value_template: '{{ value_json.filename }}'
      state_topic: creality/halotone
      icon: mdi:file-chart-outline

    - name: Halot One current slice
      value_template: '{{ value_json.curSliceLayer }}'
      state_topic: creality/halotone
      icon: mdi:bread-slice-outline

    - name: Halot One percentage done
      value_template: >
        {% if (value_json.printStatus) == 'Print Complete' %}
          100
        {% elif (value_json.curSliceLayer) == '0' %}
          0
        {% else %}
          {{ (value_json.curSliceLayer | int / value_json.sliceLayerCount | int)*100 }}
        {% endif %}
      unit_of_measurement: '%'
      icon: mdi:percent-outline
      state_topic: creality/halotone

    - name: Halot One print remaining time
      value_template: >
       {% if (value_json.printRemainTime) == '' %}
        0
       {% else %}
        {{ value_json.printRemainTime }}
       {% endif %}
      device_class: duration
      icon: mdi:circle-slice-7
      unit_of_measurement: min
      state_topic: creality/halotone
```