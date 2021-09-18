from adafruit_magtag.magtag import MagTag
from adafruit_progressbar.progressbar import ProgressBar
import ssl
import wifi
import microcontroller
import board
import alarm
import time

def setup_display():
    print("Setup Display")
    
    magtag.add_text(
        text_font="/fonts/ncenR14.pcf",
        text_position=((magtag.graphics.display.width // 2) - 1, 8,),
        text_anchor_point=(0.5, 0.5),
        is_data=False,
    )  # Title

    magtag.add_text(
        text_font="/fonts/ncenR14.pcf",
        text_position=((magtag.graphics.display.width // 2) - 1, 23,),
        text_anchor_point=(0.5, 0.5),
        is_data=False,
    )  # Date

    magtag.add_text(
        text_font="/fonts/ncenR14.pcf",
        text_position=((magtag.graphics.display.width // 2) - 1, 40,),
        text_anchor_point=(0.5, 0.5),
        is_data=False,
    )  # Vaccinated text

    magtag.add_text(
        text_font="/fonts/ncenR14.pcf",
        text_position=((magtag.graphics.display.width // 2) - 1, 85,),
        text_anchor_point=(0.5, 0.5),
        is_data=False,
    )  # Fully vaccinated text


    magtag.graphics.set_background("/bmps/background.bmp")


def setup_progress_bars(bar1Percent, bar2Percent):
    print("Setup Progress Bars")

    BAR_WIDTH = magtag.graphics.display.width - 80
    BAR_HEIGHT = 25
    BAR_X = magtag.graphics.display.width // 2 - BAR_WIDTH // 2

    progressBarDose1 = ProgressBar(
        BAR_X, 50, BAR_WIDTH, BAR_HEIGHT, 1.0, bar_color=0x999999, outline_color=0x000000
    )

    progressBarVaccinationComplete = ProgressBar(
        BAR_X, 95, BAR_WIDTH, BAR_HEIGHT, 1.0, bar_color=0x999999, outline_color=0x000000
    )

    progressBarDose1.progress = bar1Percent / 100.0
    progressBarVaccinationComplete.progress = bar2Percent / 100.0

    magtag.graphics.splash.append(progressBarDose1)
    magtag.graphics.splash.append(progressBarVaccinationComplete)


# Neopixel brightness will be determined by percentage
def update_neopixels(percentage):
    print("Update NeoPixels")

    for i in range(4):
        magtag.peripherals.neopixels[i] = 0

    n = int(percentage // 25)
    for j in range(n):
        magtag.peripherals.neopixels[3 - j] = (128, 0, 0)

    magtag.peripherals.neopixels[3 - n] = (int(((percentage / 25) % 1) * 128), 0, 0)


def handle_pin_alarms(pinAlarm):
    print("Handle Pin Alarms")
    print(type(alarm.wake_alarm))
    print(alarm.wake_alarm.pin)

    if alarm.wake_alarm.pin == board.BUTTON_A:
        # toggle saved state
        alarm.sleep_memory[0] = alarm.sleep_memory[0] - 1
    elif alarm.wake_alarm.pin == board.BUTTON_D:
        # toggle saved state
        alarm.sleep_memory[0] = alarm.sleep_memory[0] + 1
    elif alarm.wake_alarm.pin == board.BUTTON_B:
        # toggle saved state
        alarm.sleep_memory[1] = alarm.sleep_memory[1] - 1
    elif alarm.wake_alarm.pin == board.BUTTON_C:
        # toggle saved state
        alarm.sleep_memory[1] = alarm.sleep_memory[1] + 1


def handle_nap(napTime):
    print("Handle nap")

    pause = alarm.time.TimeAlarm(
                monotonic_time = time.monotonic() + napTime
            )
    sleep_alarm = [pause]
    alarms = sleep_alarm + lightSleepPinAlarms

    print(f"Napping for {napTime} seconds")
    wakeAlarm = alarm.light_sleep_until_alarms(*alarms)
    print(wakeAlarm)


# Set up where we'll be fetching data from
DATA_SOURCE = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/United%20States.csv"
cdcJsonVaccineDataUrl = "https://covid.cdc.gov/covid-data-tracker/COVIDData/getAjaxData?id=vaccination_data"
# Find data for other countries/states here:
# https://github.com/owid/covid-19-data/tree/master/public/data/vaccinations

if alarm.wake_alarm != None and isinstance(alarm.wake_alarm, alarm.pin.PinAlarm):
    handle_pin_alarms(alarm.wake_alarm)

print(f"sleep memory 0: {alarm.sleep_memory[0]}")
print(f"sleep memory 1: {alarm.sleep_memory[1]}")

# set up pin alarms
allButtons = (board.BUTTON_A, board.BUTTON_B, board.BUTTON_C, board.BUTTON_D)
lightSleepPinAlarms = [alarm.pin.PinAlarm(pin=pin, value=False, pull=True) for pin in allButtons]
deepSleepButtons = (board.BUTTON_A, board.BUTTON_D)  # pick any two
deepSleepPinAlarms = [alarm.pin.PinAlarm(pin=pin, value=False, pull=True) for pin in deepSleepButtons]

try:
    magtag = MagTag(url=cdcJsonVaccineDataUrl, json_path=["vaccination_data"])
    magtag.network.connect(20)
    magtag.peripherals.neopixel_disable = False

    vaccinationData = magtag.fetch(timeout=60)
    
    setup_display()

    while(True):
        location = alarm.sleep_memory[0]
        totalPopulation = vaccinationData[location]["Census2019"]
        locationLongname = vaccinationData[location]["LongName"]
        dosesAdministered = vaccinationData[location]["Doses_Administered"]
        vaccinatedDose1 = vaccinationData[location]["Administered_Dose1_Pop_Pct"]
        vaccinationComplete = vaccinationData[location]["Series_Complete_Pop_Pct"]
        date = vaccinationData[location]["Date"]

        magtag.set_text(f"{locationLongname} Vaccination Rates", 0, False)
        magtag.set_text(f"{date} Doses: {dosesAdministered:,d}", 1, False)
        magtag.set_text(f"Vaccinated: {vaccinatedDose1}%", 2, False)
        magtag.set_text(f"Fully Vaccinated: {vaccinationComplete}%", 3, False)

        setup_progress_bars(vaccinatedDose1, vaccinationComplete)

        magtag.refresh()

        update_neopixels(vaccinationComplete)
        handle_nap(10)

        if isinstance(alarm.wake_alarm, alarm.time.TimeAlarm):
            break

        while(isinstance(alarm.wake_alarm, alarm.pin.PinAlarm)):
            handle_pin_alarms(alarm.wake_alarm)
            handle_nap(1)

    seconds_to_sleep = 24 * 60 * 60  # Sleep for one day
    pause = alarm.time.TimeAlarm(
                monotonic_time = time.monotonic() + seconds_to_sleep
            )
    print(f"Sleeping for {seconds_to_sleep} seconds unless button pressed")
    sleep_alarm = [pause]
    #magtag.exit_and_deep_sleep(seconds_to_sleep)

    magtag.peripherals.neopixel_disable = True
    magtag.peripherals.speaker_disable = True

    alarms = sleep_alarm + deepSleepPinAlarms
    alarm.exit_and_deep_sleep_until_alarms(*alarms)

except (ValueError, RuntimeError, ConnectionError) as e:
    print("Some error occured, retrying! - ", e)
    magtag.exit_and_deep_sleep(1)
