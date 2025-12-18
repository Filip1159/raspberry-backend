import asyncio
import json
import os
import threading
from time import sleep
from typing import List, Dict
from datetime import datetime, timedelta
from melody_player import MelodyPlayer


ALARMS_FILE = './alarms.json'


DAY_TO_INT = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def load_schedule() -> List[Dict]:
    if not (os.path.exists(ALARMS_FILE) and os.path.exists(ALARMS_FILE)):
        raise FileNotFoundError("Alarms config file doesn't exist")

    with open(ALARMS_FILE, "r") as f:
        return json.load(f)


class AlarmManager:
    def __init__(self):
        self.__thread: threading.Thread | None = None
        self.__lock = threading.Lock()
        self.__stop_event = threading.Event()
        self.__schedule: List[Dict] = []
        self.player = MelodyPlayer(15)
        self.reload()


    def reload(self):
        with self.__lock:
            self.__stop_current_thread()
        
            self.__schedule = load_schedule()
            next_run, alarm = self.__find_next_run(self.__schedule)
            self.__stop_event.clear()

            self.__thread = threading.Thread(
                target=self.__run_and_reschedule,
                args=(next_run, alarm, ),
                daemon=True
            )
            self.__thread.start()

    
    def __find_next_run(self, schedule: List[Dict]) -> (datetime, Dict):
        now = datetime.now()
        candidates = []

        for entry in schedule:
            target_weekday = DAY_TO_INT[entry["day"]]
            target_time = now.replace(
                hour=entry["hour"],
                minute=entry["minute"],
                second=0,
                microsecond=0,
            )

            days_ahead = (target_weekday - now.weekday()) % 7
            run_time = target_time + timedelta(days=days_ahead)

            if run_time <= now:
                run_time += timedelta(days=7)

            candidates.append((run_time, entry))

        return min(candidates, key = lambda t: t[0])


    def __run_and_reschedule(self, run_at: datetime, alarm: Dict):
        while not self.__stop_event.is_set():
            delay = (run_at - datetime.now()).total_seconds()

            if delay > 0:
                stopped = self.__stop_event.wait(timeout=delay)
                if stopped:
                    return

            threading.Thread(
                target=self.__run_action_safe,
                args=(alarm, ),
                daemon=True
            ).start()

            with self.__lock:
                run_at, alarm = self.__find_next_run(self.__schedule)
    

    def __run_action_safe(self, alarm: Dict):
        try:
            self.__player.play(alarm['melody'])
        except Exception as e:
            print("Alarm action failed:", e)


    def __stop_current_thread(self):
        if self.__thread and self.__thread.is_alive():
            self.__stop_event.set()
            self.__thread.join()


alarm_manager = AlarmManager()
