import click
import adafruit_bme680
from adafruit_pm25.i2c import PM25_I2C
import board
import json

i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
pm25 = PM25_I2C(i2c)


@click.command()
def cli():
    pmdata = pm25.read()
    return json.dumps(dict(
        meterological=dict(
            temperature=bme680.temperature,
            humidity=bme680.humidity,
            pressure=bme680.pressure
        ),
        air_quality={
            'voc':bme680.gas,
            'pm10':pmdata['particles 100um'],
            'pm2.5':pmdata['particles 25um']
        }
    ))


if __name__ == '__main__':
    print(cli())