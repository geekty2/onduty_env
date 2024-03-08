import mysql.connector
from datetime import datetime, timedelta
from shablons import data_sources, scheme, big_naryad, small_naryad, db_config, ENTER_BD
import pprint


class NaryadScheduler:
    def __init__(self, data_sources, scheme, big_naryad, small_naryad, db_config, enter_bd):
        self.data_sources = data_sources
        self.scheme = scheme
        self.enter_bd = enter_bd
        self.big_naryad = big_naryad
        self.small_naryad = small_naryad
        self.db_config = db_config
        self.current_date = datetime.now().date()
        self.current_week_dates = self.get_current_week_dates()
        self.group_count = {11: 26, 12: 24, 13: 26, 14: 20, 15: 21}  # Кількість людей в кожній групі
        # self.group_participation = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}  # Облік заступників по групах
        self.group_iterator = None
        self.current_group = 11
        self.group_participation = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}

    def get_current_week_dates(self):
        weekday = self.current_date.weekday()
        start_of_week = self.current_date - timedelta(days=weekday)
        current_week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
        return current_week_dates

    def get_participation(self):
        for group, count in self.group_participation.items():
            percentage = (count / self.group_count[group]) * 100 if self.group_count[group] else 0
            print(f"Група {group}: {percentage:.2f}% ({count}/{self.group_count[group]})")

    def write_change_to_participation(self, query):
        for i in query:
            self.group_participation[i[3]] += 1

    def check_current_group(self):
        ...

    def regulate_assignment(self, person_list, count):
        temp = []
        for i in person_list:
            key_with_min_value = min(self.group_participation, key=self.group_participation.get)
            print(key_with_min_value)
            if i[3] == key_with_min_value:
                # Це не викличе зміни, якщо ключ відсутній, але також не викине помилку.
                self.group_participation[i[3]] = self.group_participation.get(i[3], 0) + 1

                # self.group_participation[i[3]] += 1
                temp.append(i)
                count -= 1
            if count == 0:
                break

        return temp

    def main_7day(self):
        result = []
        sorted_query = None
        for date in self.current_week_dates:
            naryad_type = self.data_sources.get(date.strftime("%d.%m"), None)

            if naryad_type == "C1":
                temp = self.big_naryad
                result.append(date.strftime("%d.%m"))
                for role, (quantity, query_key) in temp.items():
                    query_result = self.get_personnel_from_database(query_key)
                    if date.isoweekday() not in [6, 7]:
                        if role in ["ЧК", "ДК", "ДЖГ"]:
                            sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[4], x[6])),
                                                                    quantity)
                            print(f"{sorted_query}, ROLE {role}")
                            self.write_porsonnel_to_database(role, sorted_query, isodate=date)
                        elif role in ["ЧНК", "ПЧНК"]:
                            sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[4], x[7])), quantity)
                            print(f"{sorted_query}, ROLE {role}")
                            self.write_porsonnel_to_database(role, sorted_query, isodate=date)
                        elif role in ["ЧП", "Ст.ЧП"]:
                            sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[8])), quantity)
                            print(f"{sorted_query}, ROLE {role}")
                            self.write_porsonnel_to_database(role, sorted_query, isodate=date)
                        self.write_change_to_participation(sorted_query)
                        result.append((role, sorted_query))
                    else:
                        if role in ["ЧК", "ДК", "ДЖГ"]:
                            sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[4], x[5], x[6])), quantity)
                            print(f"{sorted_query}, ROLE {role}")
                            self.write_porsonnel_to_database(role, sorted_query, isodate=date)
                        elif role in ["ПЧНК", "ЧНК"]:
                            sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[4], x[5], x[7])), quantity)
                            print(f"{sorted_query}, ROLE {role}")
                            self.write_porsonnel_to_database(role, sorted_query, isodate=date)
                        elif role in ["ЧП", "Ст.ЧП"]:
                            sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[8], x[9])), quantity)
                            print(f"{sorted_query}, ROLE {role}")
                            self.write_porsonnel_to_database(role, sorted_query, isodate=date)
                        self.write_change_to_participation(sorted_query)
                        result.append((role, sorted_query))

            else:
                temp = self.small_naryad
                result.append(date.strftime("%d.%m"))
                for role, (quantity, query_key) in temp.items():
                    query_result = self.get_personnel_from_database(query_key)
                    if date.isoweekday() not in [6, 7]:
                        sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[4], x[6])), quantity)
                        print(f"{sorted_query}, ROLE {role}")
                        self.write_porsonnel_to_database(role, sorted_query, isodate=date)
                    else:
                        sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[4], x[5], x[6])), quantity)
                        print(f"{sorted_query}, ROLE {role}")
                        self.write_porsonnel_to_database(role, sorted_query, isodate=date)
                    result.append((role, sorted_query))
                pprint.pprint(result, depth=3)
                result.clear()
        self.get_participation()

    def get_personnel_from_database(self, query_key):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        cursor.execute(self.scheme[query_key])
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    def connect_and_write(self, query):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    def write_porsonnel_to_database(self, role, query, isodate):
        isodate = isodate.isoweekday()
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        for i in query:
            if isodate not in [6, 7]:
                try:
                    cursor.execute(self.enter_bd[role].format(pib=repr(i[0])))
                    connection.commit()
                    print('sql request OK', role)
                except Exception as ex:
                    print("EXCEPTION", ex)
            else:
                try:
                    cursor.execute(self.enter_bd[role + "1"].format(pib=repr(i[0])))
                    connection.commit()
                    print('sql request OK', role)

                except Exception as ex:
                    print("EXCEPTION", ex)

        connection.commit()
        cursor.close()
        connection.close()

    def reset_bd(self):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE last.kurs SET `naryad` = 0, `naryad_sb` = 0, `kurs` = 0, `nk` = 0, `chepe` = 0, `chepe_sb` = 0;")
        connection.commit()
        cursor.close()
        connection.close()


scheduler = NaryadScheduler(data_sources, scheme, big_naryad, small_naryad, db_config, ENTER_BD)
scheduler.main_7day()
# scheduler.reset_bd()
