import click
import adafruit_bme680
from adafruit_pm25.i2c import PM25_I2C
import board
import json
from math import log



i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
pm25 = PM25_I2C(i2c)

ccs811 = False

try:
    from adafruit_ccs811 import CCS811
    ccs811 = CCS811(i2c)
except (ImportError, ValueError):
    pass

def with_units(val, unit):
    return {"value":val, "units":unit}


def get():
    pmdata = pm25.read()
    return dict(
        meterological=dict(
            temperature=with_units(bme680.temperature, 'C'),
            humidity=with_units(bme680.humidity, '%'),
            pressure=with_units(bme680.pressure, 'hPa')
        ),
        air_quality={
            'voc':dict(
                quality=log(bme680.gas) + 0.04 * bme680.humidity,
                Eco2=with_units(ccs811.eco2, 'PPM') if ccs811 else with_units(bme680.gas, 'Ω'),
                TVOC=with_units(ccs811.tvoc, 'PPB') if ccs811 else with_units(bme680.gas, 'Ω'),
                gas=with_units(bme680.gas, 'Ω')
            ),
            'pm10':pmdata['particles 100um'],
            'pm2.5':pmdata['particles 25um']
        }
    )

@click.command()
def cli():
    print(json.dumps(get()))


if __name__ == '__main__':
    cli()