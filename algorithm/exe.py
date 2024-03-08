import mysql.connector
from datetime import datetime, timedelta
from shablons import data_sources, scheme, big_naryad, small_naryad, db_config, ENTER_BD
import pprint
import random


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
        self.group_part = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}  # Облік заступників по групах
        self.group_count_per_percent = {11: 3.8461538462, 12: 4.1666666667, 13: 3.8461538462, 14: 4, 15: 4.7619047619}
        self.group_participation = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}

    def get_current_week_dates(self):
        weekday = self.current_date.weekday()
        start_of_week = self.current_date - timedelta(days=weekday)
        current_week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
        return current_week_dates

    def get_participation(self):
        # temp = []
        # print("\nВідцоток людей в групі")
        #
        # for group, percentage in self.group_participation.items():
        #     print(f"Група {group}: {percentage:.2f}%")
        #     temp.append([group, percentage])
        #
        # total_people = sum(self.group_count.values())
        # print(f"\nЗагальна к-сть людей {total_people}")
        # # print(temp)
        # return temp
        print(self.group_participation)

    def regulate_assignment(self, person_list, count):
        temp = []
        while count != 0:
            key_with_min_value = min(self.group_participation, key=self.group_participation.get)

            # qwe = sorted(person_list, key=lambda x: x[3])
            for i in person_list:

                if i[3] == key_with_min_value:
                    self.group_participation[key_with_min_value] += self.group_count_per_percent[key_with_min_value]
                    self.group_part[key_with_min_value] += 1
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
                        elif role in ["ЧНК", "ПЧНК"]:
                            sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[4], x[7])),
                                                                    quantity)
                        elif role in ["ЧП", "Ст.ЧП"]:
                            sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[8])),
                                                                    quantity)
                        print(f"{sorted_query}, ROLE {role}")
                        self.write_porsonnel_to_database(role, sorted_query, isodate=date)

                        result.append((role, sorted_query))
                    else:
                        if role in ["ЧК", "ДК", "ДЖГ"]:
                            sorted_query = self.regulate_assignment(
                                sorted(query_result, key=lambda x: (x[4], x[5], x[6])), quantity)
                        elif role in ["ПЧНК", "ЧНК"]:
                            sorted_query = self.regulate_assignment(
                                sorted(query_result, key=lambda x: (x[4], x[5], x[7])), quantity)
                        elif role in ["ЧП", "Ст.ЧП"]:
                            sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[8], x[9])),
                                                                    quantity)
                        print(f"{sorted_query}, ROLE {role}")
                        self.write_porsonnel_to_database(role, sorted_query, isodate=date)

                        result.append((role, sorted_query))

            else:
                temp = self.small_naryad
                result.append(date.strftime("%d.%m"))
                for role, (quantity, query_key) in temp.items():
                    query_result = self.get_personnel_from_database(query_key)
                    if date.isoweekday() not in [6, 7]:
                        sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[4], x[6])),
                                                                quantity)
                    else:
                        sorted_query = self.regulate_assignment(sorted(query_result, key=lambda x: (x[4], x[5], x[6])),
                                                                quantity)
                    print(f"{sorted_query}, ROLE {role}")
                    self.write_porsonnel_to_database(role, sorted_query, isodate=date)
                    result.append((role, sorted_query))
                pprint.pprint(result, depth=3)
                result.clear()
            print(len(sorted_query))
        self.get_participation()

    def get_personnel_from_database(self, query_key):
        connection = mysql.connector.connect(**self.db_config)
        cursor = connection.cursor()
        cursor.execute(self.scheme[query_key])
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    # def connect_and_write(self, query):
    #     connection = mysql.connector.connect(**self.db_config)
    #     cursor = connection.cursor()
    #     cursor.execute(query)
    #     result = cursor.fetchall()
    #     cursor.close()
    #     connection.close()
    #     return result

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
print(scheduler.group_participation)
print(scheduler.group_part)
