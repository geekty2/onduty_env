
# Example usage:
data_sources = {
    "04.03": "C0",
    "05.03": "C1",
    "06.03": "C2",
    "07.03": "C0",
    "08.03": "C1",
    "09.03": "C0",
    "10.03": "МК"
}

scheme = {
    "get_sergant": "SELECT * FROM last.kurs WHERE `rank` = 'с-т';",
    "get_kursant_boy": "SELECT * FROM last.kurs WHERE `rank` = 'сол.' AND `sex` = 'Чоловік';",
    "get_girl": "SELECT * FROM last.kurs WHERE `rank` = 'сол.' AND `sex` = 'Жінка';"
}

big_naryad = {
    "ЧК": (1, "get_sergant"),
    "ДК": (2, "get_kursant_boy"),
    "ДЖГ": (1, "get_girl"),
    "ЧНК": (1, "get_sergant"),
    "ПЧНК": (3, "get_kursant_boy"),
    "Ст.ЧП": (1, "get_kursant_boy"),
    "ЧП": (9, "get_kursant_boy")
}
small_naryad = {
    "ЧК": (1, "get_sergant"),
    "ДК": (2, "get_kursant_boy"),
    "ДЖГ": (1, "get_girl")
}

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '72943618',
    'database': 'last'
}
ENTER_BD = {
    "ЧК": "UPDATE last.kurs SET `kurs` = `kurs` + 1,`naryad` = `naryad` + 1 WHERE `pib` = {pib};",
    "ДК": "UPDATE last.kurs SET `kurs` = `kurs` + 1,`naryad` = `naryad` + 1 WHERE `pib` = {pib};",
    "ДЖГ": "UPDATE last.kurs SET `kurs` = `kurs` + 1,`naryad` = `naryad` + 1 WHERE `pib` = {pib};",
    "ЧНК": "UPDATE last.kurs SET `nk` = `nk` + 1,`naryad` = `naryad` + 1 WHERE `pib` = {pib};",
    "ПЧНК": "UPDATE last.kurs SET `nk` = `nk` + 1,`naryad` = `naryad` + 1 WHERE `pib` = {pib};",
    "Ст.ЧП": "UPDATE last.kurs SET `chepe` = `chepe` + 1 WHERE `pib` = {pib};",
    "ЧП": "UPDATE last.kurs SET `chepe` = `chepe` + 1 WHERE `pib` = {pib};",

    # субота
    "ЧК1": "UPDATE last.kurs SET `kurs` = `kurs` + 1,`naryad` = `naryad` + 1,`naryad_sb` = `naryad_sb` + 1 WHERE `pib` = {pib};",
    "ДК1": "UPDATE last.kurs SET `kurs` = `kurs` + 1,`naryad` = `naryad` + 1,`naryad_sb` = `naryad_sb` + 1  WHERE `pib` = {pib};",
    "ДЖГ1": "UPDATE last.kurs SET `kurs` = `kurs` + 1,`naryad` = `naryad` + 1,`naryad_sb` = `naryad_sb` + 1  WHERE `pib` = {pib};",
    "ЧНК1": "UPDATE last.kurs SET `nk` = `nk` + 1,`naryad` = `naryad` + 1,`naryad_sb` = `naryad_sb` + 1  WHERE `pib` = {pib};",
    "ПЧНК1": "UPDATE last.kurs SET `nk` = `nk` + 1,`naryad` = `naryad` + 1,`naryad_sb` = `naryad_sb` + 1  WHERE `pib` = {pib};",
    "Ст.ЧП1": "UPDATE last.kurs SET `chepe` = `chepe` + 1,`chepe_sb` = `chepe_sb` + 1  WHERE `pib` = {pib};",
    "ЧП1": "UPDATE last.kurs SET `chepe` = `chepe` + 1,`chepe_sb` = `chepe_sb` + 1  WHERE `pib` = {pib};"

}
